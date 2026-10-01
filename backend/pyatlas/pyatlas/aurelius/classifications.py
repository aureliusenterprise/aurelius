"""Classification management of the Aurelius frontend (administrators): the tenant's classification definitions
with their use, and creating, changing and deleting them.

A classification is an Atlas classification type definition (``<prefix>_typedefs``, per tenant).  The frontend's
display names live in the definition's ``options`` (``displayName``, ``displayName.<language>``), so they travel with
the definition (export/import) and need no translation files.  Rules on top of Atlas:

* the technical name is unique among *all* type names of the tenant, also ignoring case (Atlas only refuses an
  exact duplicate), and is fixed once created (Atlas cannot rename a type);
* the display names are unique among the classifications, per language and ignoring case;
* a classification that is still attached to an entity (directly or propagated) cannot be deleted.

Authorization stays with the type definition store: creating, changing and deleting a type needs the type
privileges (ROLE_ADMIN in the default policy), reading the list the type-read privilege every role has.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..errors import AtlasBaseException, AtlasErrorCode

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
LANGUAGES = ("nl-NL",)                     # display name languages besides the default (English)
OPTION_KEYS = ("displayName",) + tuple(f"displayName.{lang}" for lang in LANGUAGES)


class ClassificationError(Exception):
    """A request the administrator can correct (shown in the form)."""

    def __init__(self, message: str, field: Optional[str] = None, status: int = 400):
        super().__init__(message)
        self.message, self.field, self.status = message, field, status


def _display_names(d: dict) -> Dict[str, str]:
    options = d.get("options") or {}
    return {k: str(options[k]).strip() for k in OPTION_KEYS if options.get(k)}


def summary(d: dict, direct: int = 0, propagated: int = 0) -> dict:
    names = _display_names(d)
    return {"name": d["name"], "displayName": names.get("displayName"),
            "displayNames": {k.split(".", 1)[1]: v for k, v in names.items() if "." in k},
            "description": d.get("description") if d.get("description") != d["name"] else None,
            "entityTypes": list(d.get("entityTypes") or []), "guid": d.get("guid"),
            "createdBy": d.get("createdBy"), "updatedBy": d.get("updatedBy"), "updateTime": d.get("updateTime"),
            "usage": {"direct": direct, "propagated": propagated}}


async def usage(services, name: str) -> Dict[str, int]:
    """Active entities that carry the classification themselves and those that got it by propagation."""
    s = services.store
    active = {"term": {"status": "ACTIVE"}}
    direct = await s.count(s.entities, {"bool": {"filter": [active, {"term": {"classificationNames": name}}]}})
    propagated = await s.count(s.entities, {"bool": {"filter": [
        active, {"term": {"propagatedClassificationNames": name}}],
        "must_not": [{"term": {"classificationNames": name}}]}})
    return {"direct": direct, "propagated": propagated}


async def list_all(services) -> List[dict]:
    reg = services.typedefs.registry
    out = []
    for name, t in sorted(reg.classifications.items(), key=lambda kv: kv[0].lower()):
        if not services.authz.is_type_allowed("type-read", t.tdef):
            continue
        u = await usage(services, name)
        out.append(summary(t.tdef, u["direct"], u["propagated"]))
    return out


def _clean_body(body: Any) -> dict:
    if not isinstance(body, dict):
        raise ClassificationError("expected a classification")
    display = body.get("displayName")
    names = body.get("displayNames") or {}
    if not isinstance(names, dict):
        raise ClassificationError("displayNames must be an object", "displayNames")
    entity_types = body.get("entityTypes") or []
    if not isinstance(entity_types, list) or not all(isinstance(t, str) for t in entity_types):
        raise ClassificationError("entityTypes must be a list of type names", "entityTypes")
    description = body.get("description")
    return {"name": str(body.get("name") or "").strip(), "displayName": str(display or "").strip(),
            "displayNames": {lang: str(names.get(lang) or "").strip() for lang in LANGUAGES},
            "description": str(description).strip() if description else "", "entityTypes": entity_types}


def _validate(reg, b: dict, existing: Optional[str]) -> None:
    if not b["displayName"]:
        raise ClassificationError("a display name is required", "displayName")
    for t in b["entityTypes"]:
        if t not in reg.entities:
            raise ClassificationError(f"unknown entity type {t}", "entityTypes")
    # display names: unique among the classifications, per language, ignoring case
    wanted = {"displayName": b["displayName"],
              **{f"displayName.{lang}": v for lang, v in b["displayNames"].items() if v}}
    for name, t in reg.classifications.items():
        if name == existing:
            continue
        theirs = _display_names(t.tdef)
        theirs.setdefault("displayName", name)
        for key, value in wanted.items():
            if theirs.get(key, "").casefold() == value.casefold() or \
                    (key == "displayName" and name.casefold() == value.casefold()):
                field = "displayName" if key == "displayName" else "displayNames"
                raise ClassificationError(f'the display name "{value}" is already used by classification {name}',
                                          field, 409)


def _options(old: Optional[dict], b: dict) -> Dict[str, str]:
    options = {k: v for k, v in ((old or {}).get("options") or {}).items() if k not in OPTION_KEYS}
    options["displayName"] = b["displayName"]
    for lang, v in b["displayNames"].items():
        if v:
            options[f"displayName.{lang}"] = v
    return options


async def create(services, body: Any, user: str) -> dict:
    b = _clean_body(body)
    services.authz.verify_type("type-create", {"name": b["name"], "category": "CLASSIFICATION"},
                               f"create classification {b['name']}")
    reg = services.typedefs.registry
    name = b["name"]
    if not NAME_RE.match(name):
        raise ClassificationError("the name must start with a letter and contain only letters, digits and _ "
                                  "(at most 64 characters)", "name")
    clash = next((n for n in reg.defs if n.casefold() == name.casefold()), None)
    if clash:
        raise ClassificationError(f"the name {name} is already used by the type {clash}", "name", 409)
    _validate(reg, b, None)
    d = {"name": name, "description": b["description"] or None, "typeVersion": "1.0",
         "options": _options(None, b), "attributeDefs": [], "superTypes": [], "entityTypes": b["entityTypes"]}
    res = await services.typedefs.create({"classificationDefs": [d]}, user)
    return summary(res["classificationDefs"][0])


async def update(services, name: str, body: Any, user: str) -> dict:
    b = _clean_body(body)
    reg = services.typedefs.registry
    t = reg.classifications.get(name)
    if t is None:
        raise ClassificationError(f"no classification {name}", None, 404)
    services.authz.verify_type("type-update", t.tdef, f"update classification {name}")
    if b["name"] and b["name"] != name:
        raise ClassificationError("the name of a classification cannot be changed", "name")
    _validate(reg, b, name)
    old = t.tdef
    d = {"name": name, "description": b["description"] or None, "options": _options(old, b),
         "attributeDefs": old.get("attributeDefs") or [], "superTypes": old.get("superTypes") or [],
         "entityTypes": b["entityTypes"], "typeVersion": old.get("typeVersion")}
    res = await services.typedefs.update({"classificationDefs": [d]}, user)
    u = await usage(services, name)
    return summary(res["classificationDefs"][0], u["direct"], u["propagated"])


async def delete(services, name: str) -> None:
    reg = services.typedefs.registry
    if name not in reg.classifications:
        raise ClassificationError(f"no classification {name}", None, 404)
    services.authz.verify_type("type-delete", reg.classifications[name].tdef, f"delete classification {name}")
    u = await usage(services, name)
    if u["direct"] or u["propagated"]:
        raise ClassificationError(
            f"{name} is still attached to {u['direct']} entities (and propagated to {u['propagated']}); "
            "remove it from them first", None, 409)
    try:
        await services.typedefs.delete_by_names([name], services.type_has_instances)
    except AtlasBaseException as e:
        if e.error_code == AtlasErrorCode.TYPE_HAS_REFERENCES:
            raise ClassificationError(f"{name} is still in use: {e.message}", None, 409) from None
        raise


__all__ = ["ClassificationError", "create", "delete", "list_all", "summary", "update", "usage"]
