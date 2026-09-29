"""Authorization, modelled on Atlas' ``AtlasAuthorizer`` / ``AtlasAuthorizationUtils``.

Two implementations are available (setting ``PYATLAS_AUTHORIZER``):

``simple`` (default)
    Atlas' ``AtlasSimpleAuthorizer``: a JSON policy file (``conf/atlas-simple-authz-policy.json``,
    same format as Atlas) maps users and groups to roles; a role grants admin, type, entity and
    relationship privileges.  Patterns are Java regular expressions matched against the whole value
    (``.*`` matches everything), exactly as in Atlas.
``none``
    Atlas' ``AtlasNoneAuthorizer``: everything is allowed.

The current user is carried in a :mod:`contextvars` variable that the authentication middleware sets
for every request, so the checks can live in the service layer (where Atlas has them) and are also
applied in background work started by a request (async import, downloads).  Code running without a
user (server start-up, model loading, schedulers) is allowed everything - like Atlas, where
``AtlasAuthorizationUtils`` allows access when there is no authenticated user.
"""
from __future__ import annotations

import contextlib
import json
import logging
import re
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from ..errors import AtlasBaseException, AtlasErrorCode

log = logging.getLogger(__name__)


class Privilege:
    TYPE_CREATE = "type-create"
    TYPE_UPDATE = "type-update"
    TYPE_DELETE = "type-delete"
    TYPE_READ = "type-read"
    ENTITY_READ = "entity-read"
    ENTITY_CREATE = "entity-create"
    ENTITY_UPDATE = "entity-update"
    ENTITY_DELETE = "entity-delete"
    ENTITY_READ_CLASSIFICATION = "entity-read-classification"
    ENTITY_ADD_CLASSIFICATION = "entity-add-classification"
    ENTITY_UPDATE_CLASSIFICATION = "entity-update-classification"
    ENTITY_REMOVE_CLASSIFICATION = "entity-remove-classification"
    ENTITY_ADD_LABEL = "entity-add-label"
    ENTITY_REMOVE_LABEL = "entity-remove-label"
    ENTITY_UPDATE_BUSINESS_METADATA = "entity-update-business-metadata"
    RELATIONSHIP_ADD = "add-relationship"
    RELATIONSHIP_UPDATE = "update-relationship"
    RELATIONSHIP_REMOVE = "remove-relationship"
    ADMIN_EXPORT = "admin-export"
    ADMIN_IMPORT = "admin-import"
    ADMIN_PURGE = "admin-purge"
    ADMIN_AUDITS = "admin-audits"
    SERVICE_NOTIFICATION_POST = "service-notification-post"


CLASSIFICATION_PRIVILEGES = {Privilege.ENTITY_ADD_CLASSIFICATION, Privilege.ENTITY_UPDATE_CLASSIFICATION,
                             Privilege.ENTITY_REMOVE_CLASSIFICATION}

# --------------------------------------------------------------------------- request context
_current_user: ContextVar[Optional[Any]] = ContextVar("pyatlas_user", default=None)
_import_in_progress: ContextVar[bool] = ContextVar("pyatlas_import_in_progress", default=False)


def set_current_user(user) -> None:
    _current_user.set(user)


def current_user():
    return _current_user.get()


def current_user_name() -> Optional[str]:
    u = _current_user.get()
    return u.name if u is not None else None


@contextlib.contextmanager
def as_user(user):
    tok = _current_user.set(user)
    try:
        yield
    finally:
        _current_user.reset(tok)


@contextlib.contextmanager
def import_in_progress():
    """Entity, type and relationship checks are skipped while an import runs (admin-import was verified)."""
    tok = _import_in_progress.set(True)
    try:
        yield
    finally:
        _import_in_progress.reset(tok)


# --------------------------------------------------------------------------- matching (Atlas semantics)
@lru_cache(maxsize=4096)
def _compiled(pattern: str):
    try:
        return re.compile(pattern)
    except re.error:
        return None


def _is_match(value: Optional[str], pattern: str) -> bool:
    if value is None:
        return True
    if pattern == ".*" or value.lower() == pattern.lower():
        return True
    rx = _compiled(pattern)
    return bool(rx and rx.fullmatch(value))


def is_match(value: Optional[str], patterns: Optional[List[str]]) -> bool:
    ret = value is None
    for p in patterns or []:
        if _is_match(value, p):
            return True
    return ret


def is_match_any(values: Set[str], patterns: Optional[List[str]]) -> bool:
    ret = not values
    if patterns:
        for v in values:
            if is_match(v, patterns):
                return True
    return ret


# --------------------------------------------------------------------------- authorizers
class NoneAuthorizer:
    name = "none"

    def admin(self, user: str, groups: Set[str], action: str) -> bool:
        return True

    def type(self, user: str, groups: Set[str], action: str, category: Optional[str], type_name: Optional[str]) -> bool:
        return True

    def entity(self, user: str, groups: Set[str], req: "EntityRequest") -> bool:
        return True

    def relationship(self, user: str, groups: Set[str], req: "RelationshipRequest") -> bool:
        return True

    def roles(self, user: str, groups: Set[str]) -> Set[str]:
        return set()


class EntityRequest:
    def __init__(self, action: str, entity_types: Set[str], entity_id: Optional[str], classifications: Set[str],
                 cls_super_types, classification: Optional[str] = None, label: Optional[str] = None,
                 business_metadata: Optional[str] = None, attribute: Optional[str] = None):
        self.action = action
        self.entity_types = entity_types
        self.entity_id = entity_id
        self.classifications = classifications
        self.cls_super_types = cls_super_types
        self.classification = classification
        self.label = label
        self.business_metadata = business_metadata
        self.attribute = attribute


class RelationshipRequest:
    def __init__(self, action: str, relationship_type: str, end1: EntityRequest, end2: EntityRequest):
        self.action = action
        self.relationship_type = relationship_type
        self.end1 = end1
        self.end2 = end2


class SimpleAuthorizer:
    """Port of ``org.apache.atlas.authorize.simple.AtlasSimpleAuthorizer``."""

    name = "simple"

    def __init__(self, policy: Dict[str, Any]):
        self.policy = policy or {}
        self.roles_def: Dict[str, Dict[str, Any]] = self.policy.get("roles") or {}
        self.user_roles: Dict[str, List[str]] = self.policy.get("userRoles") or {}
        self.group_roles: Dict[str, List[str]] = self.policy.get("groupRoles") or {}
        # add the type-read privilege where type-create/update/delete is granted
        for role in self.roles_def.values():
            for perm in role.get("typePermissions") or []:
                privs = perm.get("privileges") or []
                if privs and Privilege.TYPE_READ not in privs and \
                        {Privilege.TYPE_CREATE, Privilege.TYPE_UPDATE, Privilege.TYPE_DELETE} & set(privs):
                    privs.append(Privilege.TYPE_READ)

    @classmethod
    def from_file(cls, path: Path) -> "SimpleAuthorizer":
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f))

    def roles(self, user: Optional[str], groups: Iterable[str]) -> Set[str]:
        out: Set[str] = set()
        if user is not None:
            out.update(self.user_roles.get(user) or [])
        for g in groups or ():
            out.update(self.group_roles.get(g) or [])
        return out

    def _perms(self, role: str, kind: str) -> List[Dict[str, Any]]:
        r = self.roles_def.get(role)
        return (r.get(kind) or []) if r else []

    def admin(self, user, groups, action) -> bool:
        for role in self.roles(user, groups):
            for p in self._perms(role, "adminPermissions"):
                if is_match(action, p.get("privileges")):
                    return True
        return False

    def type(self, user, groups, action, category, type_name) -> bool:
        for role in self.roles(user, groups):
            for p in self._perms(role, "typePermissions"):
                if is_match(action, p.get("privileges")) and is_match(category, p.get("typeCategories")) \
                        and is_match(type_name, p.get("typeNames")):
                    return True
        return False

    def entity(self, user, groups, req: EntityRequest) -> bool:
        to_authz = set(req.classifications)
        for role in self.roles(user, groups):
            for p in self._perms(role, "entityPermissions"):
                if not (is_match(req.action, p.get("privileges"))
                        and is_match_any(req.entity_types, p.get("entityTypes"))
                        and is_match(req.entity_id, p.get("entityIds"))
                        and is_match(req.attribute, p.get("attributes"))
                        and self._label_match(req, p) and self._bm_match(req, p) and self._cls_match(req, p)):
                    continue
                to_authz = {c for c in to_authz
                            if not is_match_any(req.cls_super_types(c), p.get("entityClassifications"))}
                if not to_authz:
                    return True
        return False

    @staticmethod
    def _label_match(req: EntityRequest, p) -> bool:
        return req.action not in (Privilege.ENTITY_ADD_LABEL, Privilege.ENTITY_REMOVE_LABEL) \
            or is_match(req.label, p.get("labels"))

    @staticmethod
    def _bm_match(req: EntityRequest, p) -> bool:
        return req.action != Privilege.ENTITY_UPDATE_BUSINESS_METADATA or is_match(req.business_metadata,
                                                                                   p.get("businessMetadata"))

    @staticmethod
    def _cls_match(req: EntityRequest, p) -> bool:
        return req.action not in CLASSIFICATION_PRIVILEGES or req.classification is None \
            or is_match(req.classification, p.get("classifications"))

    def relationship(self, user, groups, req: RelationshipRequest) -> bool:
        end1_cls, end2_cls = set(req.end1.classifications), set(req.end2.classifications)
        ok1 = ok2 = False
        for role in self.roles(user, groups):
            for p in self._perms(role, "relationshipPermissions"):
                if not (is_match(req.relationship_type, p.get("relationshipTypes"))
                        and is_match(req.action, p.get("privileges"))):
                    continue
                if not ok1 and is_match_any(req.end1.entity_types, p.get("end1EntityType")) \
                        and is_match(req.end1.entity_id, p.get("end1EntityId")):
                    end1_cls = {c for c in end1_cls
                                if not is_match_any(req.end1.cls_super_types(c), p.get("end1EntityClassification"))}
                    ok1 = not end1_cls
                if not ok2 and is_match_any(req.end2.entity_types, p.get("end2EntityType")) \
                        and is_match(req.end2.entity_id, p.get("end2EntityId")):
                    end2_cls = {c for c in end2_cls
                                if not is_match_any(req.end2.cls_super_types(c), p.get("end2EntityClassification"))}
                    ok2 = not end2_cls
        return ok1 and ok2


# --------------------------------------------------------------------------- service used by the other layers
def _header_classification_names(h: Optional[dict]) -> Set[str]:
    if not h:
        return set()
    if h.get("classificationNames") is not None:
        return set(h["classificationNames"])
    if h.get("allClassificationNames") is not None:
        return set(h["allClassificationNames"])
    names = {c.get("typeName") for c in (h.get("classifications") or []) if isinstance(c, dict)}
    names |= {c.get("typeName") for c in (h.get("propagatedClassifications") or []) if isinstance(c, dict)}
    return {n for n in names if n}


def _policy_name(user) -> Optional[str]:
    """The user name the policy's ``userRoles`` apply to: only users of the users file.  A Keycloak user named
    like a file user (e.g. ``admin``) gets only the roles of its token."""
    return None if getattr(user, "source", "file") == "oidc" else user.name


class AuthzService:
    """Atlas' ``AtlasAuthorizationUtils`` bound to a type registry."""

    def __init__(self, authorizer, typedefs):
        self.authorizer = authorizer
        self.typedefs = typedefs

    @property
    def enabled(self) -> bool:
        return not isinstance(self.authorizer, NoneAuthorizer)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _user():
        u = _current_user.get()
        if u is None or not getattr(u, "name", None):
            return None
        return u

    def _cls_super_types(self, name: str) -> Set[str]:
        t = self.typedefs.registry.classifications.get(name)
        return t.type_and_all_super_types() if t else {name}

    def _entity_request(self, action: str, header: Optional[dict], classification: Optional[str] = None,
                        label: Optional[str] = None, bm: Optional[str] = None,
                        attribute: Optional[str] = None) -> EntityRequest:
        reg = self.typedefs.registry
        types: Set[str] = set()
        entity_id: Optional[str] = None
        if header is not None:
            tname = header.get("typeName")
            if tname:
                t = reg.entities.get(tname)
                types = t.type_and_all_super_types() if t else {tname}
            attrs = header.get("attributes") or {}
            t = reg.entities.get(tname) if tname else None
            uniq = list(t.unique_attributes) if t and t.unique_attributes else ["qualifiedName"]
            val = None
            for u in uniq:
                val = attrs.get(u)
                if val is None and u == "qualifiedName":
                    val = (header.get("uniqueAttributes") or {}).get(u)
                if val is not None:
                    break
            entity_id = "" if val is None else str(val)
        return EntityRequest(action, types, entity_id, _header_classification_names(header), self._cls_super_types,
                             classification, label, bm, attribute)

    def _deny(self, user, message: str):
        raise AtlasBaseException(AtlasErrorCode.UNAUTHORIZED_ACCESS, user.name, message)

    # ------------------------------------------------------------------ admin
    def is_admin_allowed(self, action: str) -> bool:
        u = self._user()
        if u is None:
            return True
        return self.authorizer.admin(_policy_name(u), u.groups, action)

    def verify_admin(self, action: str, message: str = "") -> None:
        if not self.is_admin_allowed(action):
            self._deny(self._user(), message)

    # ------------------------------------------------------------------ types
    def is_type_allowed(self, action: str, typedef: Optional[dict]) -> bool:
        u = self._user()
        if u is None or _import_in_progress.get():
            return True
        cat = typedef.get("category") if typedef else None
        name = typedef.get("name") if typedef else None
        return self.authorizer.type(_policy_name(u), u.groups, action, cat, name)

    def verify_type(self, action: str, typedef: Optional[dict], message: str = "") -> None:
        if not self.is_type_allowed(action, typedef):
            self._deny(self._user(), message)

    def filter_types_def(self, types_def: dict) -> dict:
        if self._user() is None or _import_in_progress.get():
            return types_def
        for k, lst in types_def.items():
            if isinstance(lst, list):
                types_def[k] = [d for d in lst if self.is_type_allowed(Privilege.TYPE_READ, d)]
        return types_def

    def filter_type_headers(self, headers: List[dict]) -> List[dict]:
        if self._user() is None:
            return headers
        return [h for h in headers if self.is_type_allowed(Privilege.TYPE_READ, h)]

    # ------------------------------------------------------------------ entities
    def is_entity_allowed(self, action: str, header: Optional[dict] = None, classification: Optional[str] = None,
                          label: Optional[str] = None, bm: Optional[str] = None,
                          attribute: Optional[str] = None) -> bool:
        u = self._user()
        if u is None or _import_in_progress.get():
            return True
        return self.authorizer.entity(_policy_name(u), u.groups,
                                      self._entity_request(action, header, classification, label, bm, attribute))

    def verify_entity(self, action: str, header: Optional[dict], message: str = "", **kw) -> None:
        if not self.is_entity_allowed(action, header, **kw):
            self._deny(self._user(), message)

    # ------------------------------------------------------------------ relationships
    def is_relationship_allowed(self, action: str, rel_type: str, end1: Optional[dict], end2: Optional[dict]) -> bool:
        u = self._user()
        if u is None or _import_in_progress.get():
            return True
        req = RelationshipRequest(action, rel_type, self._entity_request(action, end1),
                                  self._entity_request(action, end2))
        return self.authorizer.relationship(_policy_name(u), u.groups, req)

    def verify_relationship(self, action: str, rel_type: str, end1: Optional[dict], end2: Optional[dict],
                            message: str = "") -> None:
        if not self.is_relationship_allowed(action, rel_type, end1, end2):
            self._deny(self._user(), message or f"{action}: type={rel_type}")

    # ------------------------------------------------------------------ scrubbing
    @staticmethod
    def scrub_header(h: dict) -> None:
        """``AtlasAuthorizer.scrubEntityHeader``: hide everything but the type of an unreadable entity."""
        h["guid"] = "-1"
        for k in ("attributes",):
            if isinstance(h.get(k), dict):
                h[k].clear()
        for k in ("classifications", "classificationNames", "meanings", "meaningNames"):
            if isinstance(h.get(k), list):
                h[k].clear()

    def scrub_if_denied(self, h: Optional[dict]) -> bool:
        """Scrub ``h`` in place when the user may not read it; returns True when scrubbed."""
        if not h or self._user() is None:
            return False
        if not self.is_entity_allowed(Privilege.ENTITY_READ, h):
            self.scrub_header(h)
            return True
        return False

    def scrub_search_result(self, result: dict) -> dict:
        if self._user() is None or not self.enabled:
            return result
        for h in result.get("entities") or []:
            self.scrub_if_denied(h)
        for ft in result.get("fullTextResult") or []:
            if isinstance(ft, dict):
                self.scrub_if_denied(ft.get("entity"))
        for h in (result.get("referredEntities") or {}).values():
            self.scrub_if_denied(h)
        return result


def build_authorizer(settings) -> Any:
    kind = (getattr(settings, "authorizer", "simple") or "simple").lower()
    if kind in ("none", "org.apache.atlas.authorize.atlasnoneauthorizer"):
        return NoneAuthorizer()
    if kind in ("simple", "org.apache.atlas.authorize.simple.atlassimpleauthorizer"):
        path = Path(settings.authz_policy_file)
        if not path.exists():
            raise RuntimeError(f"authorization policy file {path} not found (PYATLAS_AUTHZ_POLICY_FILE)")
        return SimpleAuthorizer.from_file(path)
    raise RuntimeError(f"unknown authorizer {kind!r}; expected 'simple' or 'none'")
