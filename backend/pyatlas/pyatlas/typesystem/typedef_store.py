"""Persistence and lifecycle of type definitions (Atlas ``TypesREST`` backend)."""
from __future__ import annotations

import asyncio
import copy
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from ..errors import AtlasBaseException, AtlasErrorCode
from ..store.es import EsStore
from .registry import (BUSINESS_METADATA, CATEGORY_LIST_KEYS, CLASSIFICATION, ENTITY, ENUM, LIST_KEY_CATEGORIES,
                       RELATIONSHIP, STRUCT, TypeRegistry, base_type_name)

log = logging.getLogger(__name__)

TYPEDEF_VERSION_DOC = "typedefs_version"
PATCHES_DOC = "typedef_patches"

SEARCH_TYPE_PARAM = {
    "enum": ENUM, "struct": STRUCT, "classification": CLASSIFICATION, "entity": ENTITY,
    "relationship": RELATIONSHIP, "business_metadata": BUSINESS_METADATA,
}


def _sys_attr(name: str, type_name: str, unique: bool = False) -> dict:
    return {"name": name, "typeName": type_name, "isOptional": False, "cardinality": "SINGLE", "valuesMinCount": 1,
            "valuesMaxCount": 1, "isUnique": unique, "isIndexable": True, "includeInNotification": False,
            "searchWeight": -1}


ENTITY_ROOT_DEF = {
    "category": "ENTITY", "name": "__ENTITY_ROOT", "description": "Root entity for system attributes",
    "typeVersion": "1.0", "version": 1, "superTypes": [], "subTypes": [], "relationshipAttributeDefs": [],
    "attributeDefs": [_sys_attr("__timestamp", "date"), _sys_attr("__modificationTimestamp", "date"),
                      _sys_attr("__modifiedBy", "string"), _sys_attr("__createdBy", "string"),
                      _sys_attr("__state", "string"), _sys_attr("__guid", "string", True),
                      _sys_attr("__historicalGuids", "string", True), _sys_attr("__typeName", "string"),
                      _sys_attr("__classificationsText", "string"), _sys_attr("__classificationNames", "string"),
                      _sys_attr("__propagatedClassificationNames", "string"), _sys_attr("__isIncomplete", "int"),
                      _sys_attr("__labels", "string"), _sys_attr("__customAttributes", "string"),
                      _sys_attr("__pendingTasks", "string")],
}

CLASSIFICATION_ROOT_DEF = {
    "category": "CLASSIFICATION", "name": "__CLASSIFICATION_ROOT", "description": "Root classification for system attributes",
    "typeVersion": "1.0", "version": 1, "superTypes": [], "subTypes": [], "entityTypes": [],
    "attributeDefs": [_sys_attr("__typeName", "string"), _sys_attr("__timestamp", "date"),
                      _sys_attr("__modificationTimestamp", "date"), _sys_attr("__modifiedBy", "string"),
                      _sys_attr("__createdBy", "string"), _sys_attr("__entityStatus", "string")],
}


def now_ms() -> int:
    return int(time.time() * 1000)


def empty_types_def() -> dict:
    return {k: [] for k in CATEGORY_LIST_KEYS.values()}


def iter_types_def(types_def: dict):
    for list_key, cat in LIST_KEY_CATEGORIES.items():
        for d in types_def.get(list_key) or []:
            yield cat, d


class TypeDefStore:
    def __init__(self, store: EsStore, check_secs: float = 5.0):
        self.store = store
        self.registry: TypeRegistry = TypeRegistry({})
        self.version = -1
        self._lock = asyncio.Lock()
        self._check_secs = check_secs
        self._last_check = 0.0
        self.authz = None  # AuthzService, set by Services

    # ------------------------------------------------------------------ loading
    async def load(self) -> None:
        defs: Dict[str, dict] = {}
        async for _id, src in self.store.scan(self.store.typedefs, {"match_all": {}}, sort_field="name"):
            defs[src["name"]] = src["def"]
        self.registry = TypeRegistry(defs)
        self.version = await self._read_version()
        self._last_check = time.monotonic()

    async def _read_version(self) -> int:
        doc = await self.store.get(self.store.meta, TYPEDEF_VERSION_DOC)
        return int(((doc or {}).get("value") or {}).get("version", 0))

    async def ensure_fresh(self) -> None:
        if time.monotonic() - self._last_check < self._check_secs:
            return
        self._last_check = time.monotonic()
        v = await self._read_version()
        if v != self.version:
            log.info("typedefs changed elsewhere (version %s -> %s), reloading", self.version, v)
            await self.load()

    async def _persist(self, changed: Dict[str, dict], deleted: Iterable[str] = ()) -> None:
        actions = []
        for name, d in changed.items():
            actions.append({"op": "index", "index": self.store.typedefs, "id": name, "doc": {
                "name": name, "guid": d.get("guid"), "category": d.get("category"),
                "serviceType": d.get("serviceType"), "superTypes": d.get("superTypes") or [],
                "updateTime": d.get("updateTime"), "def": d}})
        for name in deleted:
            actions.append({"op": "delete", "index": self.store.typedefs, "id": name})
        res = await self.store.bulk(actions, refresh="true")
        errs = [r for r in res if r["error"] and not (r["op"] == "delete" and r["status"] == 404)]
        if errs:
            raise AtlasBaseException(AtlasErrorCode.INTERNAL_ERROR, f"failed to persist typedefs: {errs[:3]}")
        self.version = await self._read_version() + 1
        await self.store.put(self.store.meta, TYPEDEF_VERSION_DOC,
                             {"kind": "system", "name": TYPEDEF_VERSION_DOC, "updateTime": now_ms(),
                              "value": {"version": self.version}}, refresh="true")

    # ------------------------------------------------------------------ queries
    def _verify(self, privilege: str, d: dict, message: str) -> None:
        if self.authz is not None:
            self.authz.verify_type(privilege, d, message)

    def get_by_name(self, name: str, category: Optional[str] = None) -> dict:
        if name == "_ALL_ENTITY_TYPES" and category in (None, ENTITY):
            return ENTITY_ROOT_DEF
        if name == "_ALL_CLASSIFICATION_TYPES" and category in (None, CLASSIFICATION):
            return CLASSIFICATION_ROOT_DEF
        d = self.registry.get_def(name)
        if d is None or (category and d.get("category") != category):
            raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, name)
        self._verify("type-read", d, f"read type {name}")
        return self.registry.api_def(name)

    def get_by_guid(self, guid: str, category: Optional[str] = None) -> dict:
        name = self.registry.by_guid.get(guid)
        if name is None:
            raise AtlasBaseException(AtlasErrorCode.TYPE_GUID_NOT_FOUND, guid)
        d = self.registry.get_def(name)
        if category and d.get("category") != category:
            raise AtlasBaseException(AtlasErrorCode.TYPE_GUID_NOT_FOUND, guid)
        self._verify("type-read", d, f"read type {guid}")
        return self.registry.api_def(name)

    def search(self, params: Dict[str, Any]) -> dict:
        out = empty_types_def()
        for name in sorted(self.registry.defs):
            if self._matches(name, params):
                d = self.registry.api_def(name)
                out[CATEGORY_LIST_KEYS[d["category"]]].append(d)
        return self.authz.filter_types_def(out) if self.authz is not None else out

    def headers(self, params: Dict[str, Any]) -> List[dict]:
        out = []
        for name in sorted(self.registry.defs):
            if self._matches(name, params):
                d = self.registry.defs[name]
                h = {"guid": d.get("guid"), "name": name, "category": d.get("category")}
                if d.get("serviceType"):
                    h["serviceType"] = d["serviceType"]
                out.append(h)
        return self.authz.filter_type_headers(out) if self.authz is not None else out

    def _matches(self, name: str, p: Dict[str, Any]) -> bool:
        d = self.registry.defs[name]
        cat = d.get("category")
        t = p.get("type")
        if t:
            want = SEARCH_TYPE_PARAM.get(str(t).lower())
            if want is None or want != cat:
                return False
        if p.get("name") and p["name"] != name:
            return False
        if p.get("serviceType") and p["serviceType"] != d.get("serviceType"):
            return False
        truthy = lambda v: str(v).lower() == "true"  # noqa: E731
        if (truthy(p.get("excludeInternalTypesAndReferences", False)) or truthy(p.get("excludeInternalTypes", False))) \
                and name.startswith("__"):
            return False
        for key, positive in (("supertype", True), ("notsupertype", False)):
            vals = p.get(key)
            if not vals:
                continue
            if isinstance(vals, str):
                vals = [vals]
            st = self.registry.struct_like(name)
            if st is None or cat not in (ENTITY, CLASSIFICATION):
                if positive:
                    return False
                continue
            has = any(v in st.all_super_types for v in vals)
            if positive and not has:
                return False
            if not positive and (has or name in vals):
                return False
        return True

    # ------------------------------------------------------------------ mutations
    async def create(self, types_def: dict, user: str) -> dict:
        async with self._lock:
            await self._reload_if_stale()
            defs = dict(self.registry.defs)
            created: Dict[str, dict] = {}
            for cat, d in iter_types_def(types_def):
                name = d.get("name")
                if not name:
                    raise AtlasBaseException(AtlasErrorCode.INVALID_TYPE_DEFINITION, "type name is missing")
                if name in defs or name in created:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_ALREADY_EXISTS, name)
                self._verify("type-create", {"name": name, "category": cat},
                             f"create {cat.lower().replace('_', '')}-def {name}")
                created[name] = self._prepare_new(cat, d, user)
            defs.update(created)
            TypeRegistry(defs)  # validates
            await self._persist(created)
            self.registry = TypeRegistry(defs)
            return self._as_types_def(created)

    async def update(self, types_def: dict, user: str, allow_attribute_removal: bool = False) -> dict:
        async with self._lock:
            await self._reload_if_stale()
            defs = dict(self.registry.defs)
            updated: Dict[str, dict] = {}
            for cat, d in iter_types_def(types_def):
                name = d.get("name")
                old = defs.get(name)
                if old is None and d.get("guid"):
                    name = self.registry.by_guid.get(d["guid"])
                    old = defs.get(name) if name else None
                if old is None:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, d.get("name"))
                if old.get("category") != cat:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_MATCH_FAILED, name, cat)
                self._verify("type-update", old, f"update {cat.lower().replace('_', '')}-def {name}")
                updated[name] = self._prepare_update(old, d, user, allow_attribute_removal)
            defs.update(updated)
            TypeRegistry(defs)
            await self._persist(updated)
            self.registry = TypeRegistry(defs)
            return self._as_types_def(updated)

    async def create_or_update(self, types_def: dict, user: str) -> dict:
        """Used by the model loader: create missing types, update those with a newer typeVersion."""
        to_create, to_update = empty_types_def(), empty_types_def()
        for cat, d in iter_types_def(types_def):
            old = self.registry.get_def(d["name"])
            if old is None:
                to_create[CATEGORY_LIST_KEYS[cat]].append(d)
            elif _version_gt(d.get("typeVersion"), old.get("typeVersion")):
                to_update[CATEGORY_LIST_KEYS[cat]].append(d)
        if any(to_create.values()):
            await self.create(to_create, user)
        if any(to_update.values()):
            await self.update(to_update, user, allow_attribute_removal=True)
        return {"created": sum(len(v) for v in to_create.values()), "updated": sum(len(v) for v in to_update.values())}

    async def delete(self, types_def: dict, has_instances) -> None:
        names = [d.get("name") for _, d in iter_types_def(types_def)]
        await self.delete_by_names(names, has_instances)

    async def delete_by_names(self, names: List[str], has_instances) -> None:
        async with self._lock:
            await self._reload_if_stale()
            defs = dict(self.registry.defs)
            names_set = set()
            for n in names:
                if n not in defs:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, n)
                self._verify("type-delete", defs[n], f"delete {str(defs[n].get('category')).lower().replace('_', '')}-def {n}")
                names_set.add(n)
            for n in names_set:
                ref = self._find_reference(n, defs, names_set)
                if ref:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_HAS_REFERENCES, f"{n} (referenced by {ref})")
                if await has_instances(n, defs[n].get("category")):
                    raise AtlasBaseException(AtlasErrorCode.TYPE_HAS_REFERENCES, n)
            for n in names_set:
                defs.pop(n)
            TypeRegistry(defs)
            await self._persist({}, deleted=names_set)
            self.registry = TypeRegistry(defs)

    async def _reload_if_stale(self) -> None:
        v = await self._read_version()
        if v != self.version:
            await self.load()

    # ------------------------------------------------------------------ helpers
    def _prepare_new(self, cat: str, d: dict, user: str) -> dict:
        d = copy.deepcopy(d)
        for k in ("subTypes", "relationshipAttributeDefs", "businessAttributeDefs"):
            d.pop(k, None)
        ts = now_ms()
        d["category"] = cat
        d.setdefault("guid", str(uuid.uuid4()))
        if not d.get("guid"):
            d["guid"] = str(uuid.uuid4())
        d["createdBy"] = d.get("createdBy") or user
        d["updatedBy"] = user
        d["createTime"] = ts
        d["updateTime"] = ts
        d["version"] = 1
        d.setdefault("typeVersion", "1.0")
        d.setdefault("description", d.get("description") or d["name"])
        if cat in (STRUCT, CLASSIFICATION, ENTITY, RELATIONSHIP, BUSINESS_METADATA):
            d.setdefault("attributeDefs", [])
            for a in d["attributeDefs"]:
                _fill_attribute_defaults(a)
        if cat in (ENTITY, CLASSIFICATION):
            d.setdefault("superTypes", [])
        if cat == CLASSIFICATION:
            d.setdefault("entityTypes", [])
        if cat == ENUM:
            for i, e in enumerate(d.get("elementDefs") or []):
                e.setdefault("ordinal", i)
        if cat == RELATIONSHIP:
            d.setdefault("relationshipCategory", "ASSOCIATION")
            d.setdefault("propagateTags", "NONE")
            for key in ("endDef1", "endDef2"):
                e = d.get(key) or {}
                e.setdefault("isContainer", False)
                e.setdefault("cardinality", "SINGLE")
                e.setdefault("isLegacyAttribute", False)
        return d

    def _prepare_update(self, old: dict, new: dict, user: str, allow_attribute_removal: bool) -> dict:
        d = self._prepare_new(old["category"], new, user)
        d["guid"] = old.get("guid")
        d["name"] = old["name"]
        d["createdBy"] = old.get("createdBy")
        d["createTime"] = old.get("createTime")
        d["version"] = int(old.get("version") or 1) + 1
        if not new.get("typeVersion"):
            d["typeVersion"] = old.get("typeVersion", "1.0")
        if not allow_attribute_removal and old.get("category") in (STRUCT, CLASSIFICATION, ENTITY, BUSINESS_METADATA):
            old_attrs = {a["name"] for a in old.get("attributeDefs") or []}
            new_attrs = {a["name"] for a in d.get("attributeDefs") or []}
            removed = old_attrs - new_attrs
            if removed:
                raise AtlasBaseException(AtlasErrorCode.INVALID_TYPE_DEFINITION,
                                         f"{old['name']}: attributes cannot be removed ({', '.join(sorted(removed))})")
        return d

    def _as_types_def(self, defs: Dict[str, dict]) -> dict:
        out = empty_types_def()
        for name, d in defs.items():
            out[CATEGORY_LIST_KEYS[d["category"]]].append(self.registry.api_def(name))
        return out

    @staticmethod
    def _find_reference(name: str, defs: Dict[str, dict], excluded: Set[str]) -> Optional[str]:
        for other, d in defs.items():
            if other in excluded:
                continue
            if name in (d.get("superTypes") or []) or name in (d.get("entityTypes") or []):
                return other
            for a in d.get("attributeDefs") or []:
                if base_type_name(a.get("typeName", "")) == name:
                    return other
                aet = (a.get("options") or {}).get("applicableEntityTypes")
                if aet and name in str(aet):
                    try:
                        if name in json.loads(aet):
                            return other
                    except (ValueError, TypeError):
                        pass
            for key in ("endDef1", "endDef2"):
                if (d.get(key) or {}).get("type") == name:
                    return other
        return None

    # ------------------------------------------------------------------ model loading
    async def load_models(self, models_dir: Path, user: str = "admin") -> None:
        if not models_dir.exists():
            log.warning("models directory %s does not exist", models_dir)
            return
        patch_doc = await self.store.get(self.store.meta, PATCHES_DOC)
        applied: Dict[str, str] = dict(((patch_doc or {}).get("value") or {}).get("applied", {}))
        details: Dict[str, dict] = dict(((patch_doc or {}).get("value") or {}).get("details", {}))
        for folder in sorted(p for p in models_dir.iterdir() if p.is_dir()):
            for f in sorted(folder.glob("*.json")):
                try:
                    types_def = json.loads(f.read_text(encoding="utf-8"))
                    res = await self.create_or_update(types_def, user)
                    if res["created"] or res["updated"]:
                        log.info("model %s: created %s, updated %s types", f.name, res["created"], res["updated"])
                except AtlasBaseException as e:
                    log.error("failed to load model %s: %s", f, e.message)
            patch_dir = folder / "patches"
            if patch_dir.is_dir():
                pending = []
                for f in sorted(patch_dir.glob("*.json")):
                    for patch in json.loads(f.read_text(encoding="utf-8")).get("patches", []):
                        if patch.get("id") and patch["id"] not in applied:
                            pending.append(patch)
                            details[patch["id"]] = {"description": patch.get("description"),
                                                    "action": patch.get("action"), "time": now_ms()}
                if pending:
                    await self._apply_patches(pending, applied, user)
                    log.info("model patches %s: %d processed", folder.name, len(pending))
        await self.store.put(self.store.meta, PATCHES_DOC, {"kind": "system", "name": PATCHES_DOC, "updateTime": now_ms(),
                                                           "value": {"applied": applied, "details": details}},
                             refresh="true")

    async def apply_patch(self, patch: dict, user: str) -> str:
        async with self._lock:
            defs = dict(self.registry.defs)
            status, changed = self._apply_patch_to_defs(defs, patch, user)
            if changed:
                defs.update(changed)
                TypeRegistry(defs)
                await self._persist(changed)
                self.registry = TypeRegistry(defs)
            return status

    async def _apply_patches(self, patches: List[dict], applied: Dict[str, str], user: str) -> None:
        """Apply a folder's patches in memory, validating each, and persist once."""
        async with self._lock:
            defs = dict(self.registry.defs)
            all_changed: Dict[str, dict] = {}
            for patch in patches:
                pid = patch["id"]
                try:
                    status, changed = self._apply_patch_to_defs(defs, patch, user)
                    if changed:
                        candidate = dict(defs)
                        candidate.update(changed)
                        TypeRegistry(candidate)
                        defs = candidate
                        all_changed.update(changed)
                except AtlasBaseException as e:
                    log.warning("patch %s failed: %s", pid, e.message)
                    status = "FAILED"
                applied[pid] = status
            if all_changed:
                await self._persist(all_changed)
                self.registry = TypeRegistry(defs)

    def _apply_patch_to_defs(self, defs: Dict[str, dict], patch: dict, user: str):
        action = patch.get("action")
        type_name = patch.get("typeName")
        old = defs.get(type_name)
        if old is None:
            raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, type_name)
        if not _patch_applicable(patch, old):
            return "SKIPPED", {}
        d = copy.deepcopy(old)
        changed: Dict[str, dict] = {type_name: d}
        if action in ("ADD_ATTRIBUTE", "ADD_MANDATORY_ATTRIBUTE"):
            existing = {a["name"] for a in d.get("attributeDefs") or []}
            for a in patch.get("attributeDefs") or []:
                if a["name"] not in existing:
                    d.setdefault("attributeDefs", []).append(_fill_attribute_defaults(dict(a)))
        elif action == "UPDATE_ATTRIBUTE":
            attrs = {a["name"]: a for a in d.get("attributeDefs") or []}
            for a in patch.get("attributeDefs") or []:
                attrs[a["name"]] = _fill_attribute_defaults(dict(a))
            d["attributeDefs"] = list(attrs.values())
        elif action == "UPDATE_ATTRIBUTE_METADATA":
            for a in d.get("attributeDefs") or []:
                if a["name"] == patch.get("attributeName"):
                    a.update(patch.get("params") or {})
        elif action == "SET_SERVICE_TYPE":
            d["serviceType"] = patch.get("serviceType")
        elif action == "UPDATE_TYPEDEF_OPTIONS":
            d.setdefault("options", {}).update(patch.get("typeDefOptions") or {})
        elif action == "UPDATE_ENUMDEF":
            values = {e["value"] for e in d.get("elementDefs") or []}
            for e in patch.get("elementDefs") or []:
                if e["value"] not in values:
                    d.setdefault("elementDefs", []).append(e)
        elif action == "ADD_SUPER_TYPES":
            for st in patch.get("superTypes") or []:
                if st not in d.setdefault("superTypes", []):
                    d["superTypes"].append(st)
        elif action == "REMOVE_LEGACY_REF_ATTRIBUTES":
            if d.get("category") != RELATIONSHIP:
                return "FAILED", {}
            params = patch.get("params") or {}
            e1, e2 = d["endDef1"], d["endDef2"]
            label = params.get("relationshipLabel")
            if not label:
                if e1.get("isLegacyAttribute") and not e2.get("isLegacyAttribute"):
                    label = f"__{e1['type']}.{e1['name']}"
                elif e2.get("isLegacyAttribute"):
                    label = f"__{e2['type']}.{e2['name']}"
                else:
                    label = d.get("relationshipLabel")
            if str(params.get("swapEnds", "false")).lower() == "true":
                d["endDef1"], d["endDef2"] = e2, e1
                e1, e2 = d["endDef1"], d["endDef2"]
            if label:
                d["relationshipLabel"] = label
            if params.get("relationshipCategory"):
                d["relationshipCategory"] = params["relationshipCategory"]
            for e in (e1, e2):
                e["isLegacyAttribute"] = False
                ent = changed.get(e["type"]) or copy.deepcopy(defs.get(e["type"]) or {})
                if ent:
                    ent["attributeDefs"] = [a for a in ent.get("attributeDefs") or [] if a["name"] != e.get("name")]
                    changed[e["type"]] = ent
        else:
            log.info("patch action %s not supported, skipping %s", action, patch.get("id"))
            return "SKIPPED", {}
        d["typeVersion"] = patch.get("updateToVersion", d.get("typeVersion"))
        ts = now_ms()
        for cd in changed.values():
            cd["updateTime"] = ts
            cd["updatedBy"] = user
            cd["version"] = int(cd.get("version") or 1) + 1
        return "APPLIED", changed


# the properties of Atlas' AtlasAttributeDef; anything else (e.g. relationshipTypeName, isLegacyAttribute, which
# belong to relationship attribute / end definitions) is dropped when a type is stored, like Atlas does
ATTRIBUTE_DEF_FIELDS = {"name", "typeName", "isOptional", "cardinality", "valuesMinCount", "valuesMaxCount",
                        "isUnique", "isIndexable", "includeInNotification", "defaultValue", "description",
                        "searchWeight", "indexType", "constraints", "options", "displayName", "isDefaultValueNull"}
MAX_COUNT = 2147483647


def _fill_attribute_defaults(a: dict) -> dict:
    """Missing properties get Atlas' defaults; for the counts the multiplicity rules of
    ``AtlasStructDefStoreV2``: SINGLE -> max 1, LIST/SET -> max Integer.MAX_VALUE, min 0 (optional) or 1.
    Explicit values are kept as given (Atlas returns them unchanged, e.g. -1 in its bundled models)."""
    for k in [k for k in a if k not in ATTRIBUTE_DEF_FIELDS]:
        del a[k]
    a.setdefault("isOptional", True)
    a.setdefault("cardinality", "SINGLE")
    if a.get("valuesMinCount") is None:
        a["valuesMinCount"] = 0 if a.get("isOptional", True) else 1
    if a.get("valuesMaxCount") is None:
        a["valuesMaxCount"] = 1 if a["cardinality"] == "SINGLE" else MAX_COUNT
    a.setdefault("isUnique", False)
    a.setdefault("isIndexable", False)
    a.setdefault("includeInNotification", False)
    a.setdefault("searchWeight", -1)
    return a


def _version_parts(v: Optional[str]) -> List[int]:
    out = []
    for p in str(v or "0").split("."):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return out


def _version_gt(a: Optional[str], b: Optional[str]) -> bool:
    return _version_parts(a) > _version_parts(b)


def _patch_applicable(patch: dict, d: dict) -> bool:
    cur = d.get("typeVersion")
    apply_to = patch.get("applyToVersion")
    return cur is None or apply_to is None or cur.lower() == apply_to.lower() or cur.startswith(apply_to + ".")
