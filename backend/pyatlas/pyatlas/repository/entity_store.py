"""Entity and relationship persistence (Atlas ``AtlasEntityStoreV2`` + ``AtlasRelationshipStoreV1``).

All mutations run through a :class:`MutationContext` which

1. resolves every entity of the request to a guid (existing guid, unique attributes, or new),
2. validates and normalises attribute values against the type registry,
3. computes relationship changes (relationships live in their own index),
4. writes everything with bulk requests, using ``if_seq_no`` optimistic locking
   for existing entity documents and ``op_type=create`` documents in the unique
   index to guarantee unique attribute values, and finally
5. recomputes classification propagation for the affected (source, tag) pairs.
"""
from __future__ import annotations

import contextlib
import copy
import logging
import re
import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode
from ..store.es import EsStore
from ..typesystem.registry import SINGLE, RelEnd, RelationshipType, TypeRegistry
from ..typesystem.values import default_for, normalize_attributes, normalize_struct, normalize_value
from .audit import AuditRepository, audit_event, details
from .converter import (build_index_fields, build_relationship_index_fields, classification_to_api, entity_header, entity_to_api, object_id,
                        relationship_to_api, strip_internal, unique_attributes_of, unique_key)
from .propagation import Pair, Propagator, pairs_of

log = logging.getLogger(__name__)

LABEL_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")
MEANING_REL = "AtlasGlossarySemanticAssignment"
REL_SOURCE_FIELDS = None


def now_ms() -> int:
    return int(time.time() * 1000)


_deferred_pairs: ContextVar[Optional[Set[Pair]]] = ContextVar("pyatlas_deferred_propagation", default=None)


def is_assigned_guid(guid: Optional[str]) -> bool:
    return bool(guid) and not str(guid).startswith("-")


@dataclass
class MutationContext:
    user: str
    now: int = field(default_factory=now_ms)
    docs: Dict[str, dict] = field(default_factory=dict)        # working entity docs
    orig: Dict[str, Optional[dict]] = field(default_factory=dict)  # original docs (None for new)
    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    partial: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)
    purged: List[str] = field(default_factory=list)
    touched: Set[str] = field(default_factory=set)             # entity docs that must be written
    guid_assignments: Dict[str, str] = field(default_factory=dict)
    rels: Dict[str, dict] = field(default_factory=dict)
    rel_orig: Dict[str, Optional[dict]] = field(default_factory=dict)
    rels_by_entity: Dict[str, Set[str]] = field(default_factory=dict)
    rels_loaded: Set[str] = field(default_factory=set)             # all relationships of these entities loaded
    rels_loaded_typed: Set[Tuple[str, str]] = field(default_factory=set)  # (entity guid, relationship type) loaded
    unique_add: Dict[str, dict] = field(default_factory=dict)
    unique_del: Set[str] = field(default_factory=set)
    audits: List[dict] = field(default_factory=list)
    prop_pairs: Set[Pair] = field(default_factory=set)
    rel_changed_entities: Set[str] = field(default_factory=set)
    purged_rels: Set[str] = field(default_factory=set)


class EntityStore:
    def __init__(self, store: EsStore, typedefs, settings):
        self.store = store
        self.typedefs = typedefs
        self.settings = settings
        self.audit = AuditRepository(store)
        self.propagator = Propagator(store, lambda: self.typedefs.registry)
        self.authz = None  # AuthzService, set by Services

    @contextlib.asynccontextmanager
    async def deferred_propagation(self, user: str):
        """Collect the classification propagation work of many mutations and do it once at the end
        (used by imports; Atlas also defers propagation while importing)."""
        pairs: Set[Pair] = set()
        tok = _deferred_pairs.set(pairs)
        try:
            yield pairs
        finally:
            _deferred_pairs.reset(tok)
        if pairs:
            await self.audit.write(await self.propagator.recompute(pairs, user))

    # ------------------------------------------------------------------ authorization helpers
    @staticmethod
    def authz_header(doc: dict) -> dict:
        """What the authorizer sees of an entity: type, attributes and all (incl. propagated) classifications."""
        names = {c.get("typeName") for c in doc.get("classifications") or []}
        names |= {c.get("typeName") for c in doc.get("propagatedClassifications") or []}
        return {"typeName": doc.get("typeName"), "attributes": doc.get("attributes") or {},
                "classificationNames": sorted(n for n in names if n)}

    def _verify(self, privilege: str, doc: Optional[dict], message: str, **kw) -> None:
        if self.authz is not None:
            self.authz.verify_entity(privilege, self.authz_header(doc) if doc is not None else None, message, **kw)

    def can_read(self, doc: dict) -> bool:
        return self.authz is None or self.authz.is_entity_allowed("entity-read", self.authz_header(doc))

    @property
    def reg(self) -> TypeRegistry:
        return self.typedefs.registry

    # ================================================================== reads
    async def _get_doc(self, guid: str) -> dict:
        doc = await self.store.get(self.store.entities, guid)
        if doc is None:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, guid)
        return doc

    async def rels_of(self, guids: Iterable[str], active_only: bool = False) -> List[dict]:
        guids = list(dict.fromkeys(guids))
        out: Dict[str, dict] = {}
        for i in range(0, len(guids), 500):
            chunk = guids[i:i + 500]
            q: Dict[str, Any] = {"bool": {"should": [{"terms": {"end1Guid": chunk}}, {"terms": {"end2Guid": chunk}}],
                                          "minimum_should_match": 1}}
            if active_only:
                q["bool"]["filter"] = [{"term": {"status": "ACTIVE"}}]
            async for rid, r in self.store.scan(self.store.relationships, q, limit=self.settings.max_relationships_per_entity):
                out[rid] = r
        return list(out.values())

    async def _others(self, doc: dict, rels: List[dict]) -> Dict[str, dict]:
        ids = set()
        for r in rels:
            ids.add(r["end1Guid"])
            ids.add(r["end2Guid"])
        ids.discard(doc["guid"])
        others = await self.store.mget(self.store.entities, ids)
        others[doc["guid"]] = doc
        return others

    async def get_by_guid(self, guid: str, min_ext_info: bool = False, ignore_relationships: bool = False) -> dict:
        doc = await self._get_doc(guid)
        self._verify("entity-read", doc, f"read entity: guid={guid}")
        return await self._with_ext_info([doc], min_ext_info, ignore_relationships, single=True)

    async def get_by_guids(self, guids: List[str], min_ext_info: bool = False, ignore_relationships: bool = False) -> dict:
        docs = await self.store.mget(self.store.entities, guids)
        missing = [g for g in guids if g not in docs]
        if missing:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, missing[0])
        for g in guids:
            self._verify("entity-read", docs[g], f"read entity: guid={g}")
        return await self._with_ext_info([docs[g] for g in dict.fromkeys(guids)], min_ext_info, ignore_relationships)

    async def _with_ext_info(self, docs: List[dict], min_ext_info: bool, ignore_relationships: bool,
                             single: bool = False) -> dict:
        reg = self.reg
        entities, referred = [], {}
        main_guids = {d["guid"] for d in docs}
        for doc in docs:
            if ignore_relationships:
                entities.append(entity_to_api(reg, doc, include_relationships=False))
                continue
            rels = await self.rels_of([doc["guid"]])
            others = await self._others(doc, rels)
            entities.append(entity_to_api(reg, doc, rels, others))
            # composition children (owned references) are returned as referred entities
            owned = []
            for r in rels:
                rt = reg.relationships.get(r["typeName"])
                if rt is None or rt.category != "COMPOSITION" or r.get("status") != "ACTIVE":
                    continue
                if r["end1Guid"] == doc["guid"] and rt.end1.is_container:
                    owned.append(r["end2Guid"])
                elif r["end2Guid"] == doc["guid"] and rt.end2.is_container:
                    owned.append(r["end1Guid"])
            for g in owned:
                if g in main_guids or g in referred or g not in others:
                    continue
                child = others[g]
                if min_ext_info:
                    referred[g] = self._min_entity(child)
                else:
                    child_rels = await self.rels_of([g])
                    child_others = await self._others(child, child_rels)
                    referred[g] = entity_to_api(reg, child, child_rels, child_others)
        if single:
            return {"entity": entities[0], "referredEntities": referred}
        return {"entities": entities, "referredEntities": referred}

    def _min_entity(self, doc: dict) -> dict:
        h = entity_header(self.reg, doc)
        return {"typeName": doc["typeName"], "attributes": h["attributes"], "guid": doc["guid"],
                "status": doc.get("status", "ACTIVE"), "classifications": h["classifications"],
                "labels": h["labels"], "isIncomplete": h["isIncomplete"]}

    async def get_header(self, guid: str) -> dict:
        doc = await self._get_doc(guid)
        self._verify("entity-read", doc, f"read entity: guid={guid}")
        return entity_header(self.reg, doc)

    async def find_guid_by_unique_attributes(self, type_name: str, unique_attrs: Dict[str, Any],
                                             include_subtypes: bool = True) -> Optional[str]:
        reg = self.reg
        et = reg.entity_type(type_name)
        types = et.type_and_all_sub_types() if include_subtypes else {type_name}
        keys = []
        for attr, value in unique_attrs.items():
            if value is None:
                continue
            a = et.attributes.get(attr)
            if a is None or not a.is_unique:
                # Atlas also allows lookups by non-unique attributes; fall back to a search
                return await self._find_by_attribute(types, attr, value)
            value = normalize_value(reg, a.type_name, value, attr)
            for t in types:
                keys.append(unique_key(t, attr, value))
        if not keys:
            return None
        found = await self.store.mget(self.store.unique, keys)
        for k in keys:
            if k in found:
                return found[k]["guid"]
        return None

    async def _find_by_attribute(self, types: Set[str], attr: str, value: Any) -> Optional[str]:
        a = self.reg.find_attribute_any_type(attr)
        if a is None:
            return None
        q = {"bool": {"filter": [{"terms": {"typeName": sorted(types)}}, {"term": {"status": "ACTIVE"}},
                                 {"term": {f"idx.{a.index_group}.{attr}": value}}]}}
        r = await self.store.search(self.store.entities, q, size=1, source=["guid"])
        hits = r["hits"]["hits"]
        return hits[0]["_id"] if hits else None

    async def get_guid_by_unique_attributes(self, type_name: str, unique_attrs: Dict[str, Any]) -> str:
        guid = await self.find_guid_by_unique_attributes(type_name, unique_attrs)
        if guid is None:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_BY_UNIQUE_ATTRIBUTE_NOT_FOUND, type_name, unique_attrs)
        return guid

    # ================================================================== create / update
    async def create_or_update(self, payload: dict, user: str, is_partial: bool = False,
                               replace_classifications: bool = False, replace_business_attributes: bool = False,
                               overwrite_business_attributes: bool = False,
                               append_relationships: Optional[bool] = None) -> dict:
        reg = self.reg
        entities: List[dict] = list(payload.get("entities") or [])
        if payload.get("entity"):
            entities.append(payload["entity"])
        referred = payload.get("referredEntities") or {}
        for k, e in referred.items():
            e = dict(e)
            e.setdefault("guid", k)
            entities.append(e)
        if not entities:
            raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, "no entities to create/update")

        ctx = MutationContext(user=user)
        # ---- phase A: resolve guids
        batch: List[Tuple[str, dict]] = []
        placeholder_map: Dict[str, str] = {}
        unique_in_batch: Dict[Tuple[str, str, str], str] = {}
        existing_guids: Set[str] = set()
        for e in entities:
            tname = e.get("typeName")
            if not tname or tname not in reg.entities:
                raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, tname)
        candidate_real = [e.get("guid") for e in entities if is_assigned_guid(e.get("guid"))]
        existing_docs = await self.store.mget(self.store.entities, candidate_real, with_version=True)
        for e in entities:
            tname = e["typeName"]
            et = reg.entities[tname]
            given = e.get("guid")
            guid = None
            if is_assigned_guid(given) and given in existing_docs:
                guid = given
            if guid is None:
                uattrs = {u: (e.get("attributes") or {}).get(u) for u in et.unique_attributes}
                uattrs = {k: v for k, v in uattrs.items() if v is not None}
                for k, v in uattrs.items():
                    bk = (tname, k, repr(v))
                    if bk in unique_in_batch:
                        guid = unique_in_batch[bk]
                        break
                if guid is None and uattrs:
                    guid = await self.find_guid_by_unique_attributes(tname, uattrs, include_subtypes=False)
                    if guid is not None:
                        existing_guids.add(guid)
                if guid is None:
                    guid = given if is_assigned_guid(given) else str(uuid.uuid4())
                for k, v in uattrs.items():
                    unique_in_batch[(tname, k, repr(v))] = guid
            if given and given != guid:
                placeholder_map[given] = guid
                ctx.guid_assignments[given] = guid
            elif given is None or not is_assigned_guid(given):
                pass
            batch.append((guid, e))
        existing_guids |= {g for g, _ in batch if g in existing_docs}
        missing = existing_guids - set(existing_docs)
        if missing:
            existing_docs.update(await self.store.mget(self.store.entities, missing, with_version=True))
        for guid, doc in existing_docs.items():
            ctx.docs[guid] = doc
            ctx.orig[guid] = copy.deepcopy(doc)
        ctx._placeholders = placeholder_map  # type: ignore[attr-defined]
        batch_guids = {g for g, _ in batch}
        ctx._batch_types = {g: e["typeName"] for g, e in batch}  # type: ignore[attr-defined]

        # merge duplicate batch entries for the same guid (last one wins per attribute)
        merged: Dict[str, dict] = {}
        order: List[str] = []
        for guid, e in batch:
            if guid in merged:
                m = merged[guid]
                m.setdefault("attributes", {}).update(e.get("attributes") or {})
                m.setdefault("relationshipAttributes", {}).update(e.get("relationshipAttributes") or {})
                for k in ("classifications", "labels", "customAttributes", "businessAttributes"):
                    if e.get(k) is not None:
                        m[k] = e[k]
            else:
                merged[guid] = copy.deepcopy(e)
                order.append(guid)


        # ---- phase B: attributes, classifications, labels ...
        rel_work: List[Tuple[str, dict]] = []
        for guid in order:
            e = merged[guid]
            rel_values = self._apply_entity(ctx, guid, e, is_partial, replace_classifications,
                                            replace_business_attributes, overwrite_business_attributes)
            if rel_values:
                rel_work.append((guid, rel_values))

        batch_unique: Dict[Tuple[str, str], List[str]] = {}
        for g in order:
            d = ctx.docs[g]
            for u in reg.entities[d["typeName"]].unique_attributes:
                v = (d.get("attributes") or {}).get(u)
                if v is not None:
                    batch_unique.setdefault((u, str(v)), []).append(g)
        ctx._batch_unique = batch_unique  # type: ignore[attr-defined]

        # ---- phase C: relationships
        for guid, rel_values in rel_work:
            await self._apply_relationship_attrs(ctx, guid, rel_values, is_partial, append_relationships,
                                                 batch_guids)

        # ---- mark updated
        for guid in order:
            self._finalize_entity(ctx, guid, is_partial)

        # ---- authorization (Atlas checks created and updated entities before committing)
        for g in ctx.created:
            self._verify("entity-create", ctx.docs[g], f"create entity: type={ctx.docs[g]['typeName']}")
        for g in ctx.updated + ctx.partial:
            if g not in ctx.created:
                self._verify("entity-update", ctx.docs[g], f"update entity: type={ctx.docs[g]['typeName']}")

        await self._commit(ctx)
        return self._mutation_response(ctx)

    def _apply_entity(self, ctx: MutationContext, guid: str, e: dict, is_partial: bool,
                      replace_classifications: bool, replace_bm: bool, overwrite_bm: bool) -> Dict[str, Any]:
        reg = self.reg
        tname = e["typeName"]
        et = reg.entities[tname]
        existing = ctx.docs.get(guid)
        if existing is not None and existing["typeName"] != tname:
            raise AtlasBaseException(AtlasErrorCode.TYPE_MATCH_FAILED, existing["typeName"], tname)

        plain: Dict[str, Any] = {}
        rel_values: Dict[str, Any] = {}
        for k, v in (e.get("attributes") or {}).items():
            a = et.attributes.get(k)
            if a is not None and not a.is_object_ref:
                plain[k] = v
            elif k in et.relationship_attributes:
                rel_values[k] = v
        for k, v in (e.get("relationshipAttributes") or {}).items():
            if k in et.relationship_attributes:
                rel_values[k] = v

        is_new = existing is None
        if is_new:
            for a in et.attributes.values():
                if a.name not in plain and not a.is_object_ref:
                    dv = default_for(reg, a)
                    if dv is not None:
                        plain[a.name] = dv
        norm = normalize_attributes(reg, et.attributes, plain, tname, check_mandatory=is_new)

        if is_new:
            doc = {
                "guid": guid, "typeName": tname, "status": "ACTIVE",
                "createdBy": ctx.user, "updatedBy": ctx.user, "createTime": ctx.now, "updateTime": ctx.now,
                "version": 0, "attributes": {}, "classifications": [], "propagatedClassifications": [],
                "labels": [], "customAttributes": {}, "businessAttributes": {},
                "isIncomplete": bool(e.get("isIncomplete", False)), "provenanceType": e.get("provenanceType", 0),
            }
            if e.get("homeId"):
                doc["homeId"] = e["homeId"]
            ctx.docs[guid] = doc
            ctx.orig[guid] = None
            ctx.rels_loaded.add(guid)
            ctx.created.append(guid)
        doc = ctx.docs[guid]
        old_attrs = copy.deepcopy(doc.get("attributes") or {})
        doc["attributes"] = {**old_attrs, **norm}
        if doc.get("isIncomplete") and not is_new and not e.get("isIncomplete", False):
            doc["isIncomplete"] = False  # shell entity becomes complete

        # unique attributes
        for u in et.unique_attributes:
            ov, nv = old_attrs.get(u), doc["attributes"].get(u)
            if not is_new and ov == nv:
                continue
            if ov is not None and not is_new:
                ctx.unique_del.add(unique_key(tname, u, ov))
            if nv is not None:
                ctx.unique_add[unique_key(tname, u, nv)] = {"guid": guid, "typeName": tname, "attribute": u, "ts": ctx.now}

        # classifications
        if e.get("classifications") is not None and (is_new or replace_classifications):
            self._set_classifications(ctx, doc, e["classifications"])
        # labels
        if e.get("labels") is not None and (is_new or "labels" in e):
            new_labels = self._validate_labels(e["labels"])
            if set(new_labels) != set(doc.get("labels") or []):
                doc["labels"] = new_labels
        if e.get("customAttributes") is not None:
            doc["customAttributes"] = self._validate_custom_attributes(e["customAttributes"])
        if e.get("businessAttributes") is not None and (is_new or replace_bm):
            bm = self._validate_business_attributes(tname, e["businessAttributes"])
            if is_new or overwrite_bm:
                doc["businessAttributes"] = bm
            else:
                cur = copy.deepcopy(doc.get("businessAttributes") or {})
                for k, v in bm.items():
                    cur.setdefault(k, {}).update(v)
                doc["businessAttributes"] = cur
        ctx.touched.add(guid)
        return rel_values

    def _finalize_entity(self, ctx: MutationContext, guid: str, is_partial: bool) -> None:
        doc = ctx.docs[guid]
        orig = ctx.orig.get(guid)
        if orig is None:
            return  # created
        changed = any(orig.get(k) != doc.get(k) for k in
                      ("attributes", "classifications", "labels", "customAttributes", "businessAttributes", "isIncomplete"))
        if changed or guid in ctx.rel_changed_entities:
            doc["updateTime"] = ctx.now
            doc["updatedBy"] = ctx.user
            doc["version"] = int(orig.get("version") or 0) + 1
            if guid not in ctx.updated and guid not in ctx.partial:
                (ctx.partial if is_partial else ctx.updated).append(guid)
        else:
            ctx.touched.discard(guid)

    # ------------------------------------------------------------------ relationships
    async def _preload_rels(self, ctx: MutationContext, guids: Iterable[str]) -> None:
        """Load all active relationships of the given entities (used when deleting them)."""
        guids = [g for g in guids if g not in ctx.rels_loaded]
        if not guids:
            return
        self._add_loaded_rels(ctx, await self.rels_of(guids, active_only=True))
        for g in guids:
            ctx.rels_loaded.add(g)
            ctx.rels_by_entity.setdefault(g, set())

    def _add_loaded_rels(self, ctx: MutationContext, rels: Iterable[dict]) -> None:
        for r in rels:
            if r["guid"] in ctx.rels:
                continue
            ctx.rels[r["guid"]] = r
            ctx.rel_orig[r["guid"]] = copy.deepcopy(r)
            for eg in (r["end1Guid"], r["end2Guid"]):
                ctx.rels_by_entity.setdefault(eg, set()).add(r["guid"])

    async def _ensure_rels(self, ctx: MutationContext, guids: Iterable[str], rel_name: str) -> None:
        """Load the active relationships of type ``rel_name`` of the given entities (cached per request)."""
        todo = [g for g in dict.fromkeys(guids) if g not in ctx.rels_loaded and (g, rel_name) not in ctx.rels_loaded_typed]
        if not todo:
            return
        for i in range(0, len(todo), 500):
            chunk = todo[i:i + 500]
            q = {"bool": {"filter": [{"term": {"typeName": rel_name}}, {"term": {"status": "ACTIVE"}}],
                          "should": [{"terms": {"end1Guid": chunk}}, {"terms": {"end2Guid": chunk}}],
                          "minimum_should_match": 1}}
            rels = [r async for _, r in self.store.scan(self.store.relationships, q,
                                                          limit=self.settings.max_relationships_per_entity)]
            self._add_loaded_rels(ctx, rels)
        for g in todo:
            ctx.rels_loaded_typed.add((g, rel_name))
            ctx.rels_by_entity.setdefault(g, set())

    async def _ensure_entity(self, ctx: MutationContext, guid: str) -> dict:
        if guid in ctx.docs:
            return ctx.docs[guid]
        doc = await self.store.get(self.store.entities, guid, with_version=True)
        if doc is None:
            raise AtlasBaseException(AtlasErrorCode.REFERENCED_ENTITY_NOT_FOUND, guid)
        ctx.docs[guid] = doc
        ctx.orig[guid] = copy.deepcopy(doc)
        return doc

    async def _resolve_ref(self, ctx: MutationContext, value: Any, expected_type: str) -> Tuple[str, str]:
        """Return (guid, typeName) for an object id / related object id / guid string."""
        reg = self.reg
        placeholders: Dict[str, str] = getattr(ctx, "_placeholders", {})
        batch_types: Dict[str, str] = getattr(ctx, "_batch_types", {})
        if isinstance(value, str):
            value = {"guid": value}
        if not isinstance(value, dict):
            raise AtlasBaseException(AtlasErrorCode.INVALID_OBJECT_ID, value)
        guid = value.get("guid")
        if guid and guid in placeholders:
            guid = placeholders[guid]
        if guid and guid in batch_types:
            return guid, batch_types[guid]
        if is_assigned_guid(guid):
            doc = await self._ensure_entity(ctx, guid)
            return guid, doc["typeName"]
        tname = value.get("typeName") or expected_type
        uattrs = value.get("uniqueAttributes")
        if not uattrs and value.get("attributes"):
            et = reg.entities.get(tname)
            if et:
                uattrs = {u: value["attributes"].get(u) for u in et.unique_attributes if value["attributes"].get(u) is not None}
        if tname and uattrs:
            if tname not in reg.entities:
                raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, tname)
            cache: Dict[Any, Tuple[str, str]] = ctx.__dict__.setdefault("_ref_cache", {})
            ckey = (tname, tuple(sorted((k, str(v)) for k, v in uattrs.items())))
            if ckey in cache:
                return cache[ckey]
            # entities created/updated in this very request
            batch_unique: Dict[Tuple[str, str], List[str]] = getattr(ctx, "_batch_unique", {})
            k0, v0 = next(iter(uattrs.items()))
            for g in batch_unique.get((k0, str(v0)), []):
                bt = batch_types.get(g)
                d = ctx.docs.get(g)
                if bt and d and reg.entities[bt].isa(tname) and \
                        all(str((d.get("attributes") or {}).get(k)) == str(v) for k, v in uattrs.items()):
                    return g, bt
            found = await self.find_guid_by_unique_attributes(tname, uattrs)
            if found:
                doc = await self._ensure_entity(ctx, found)
                cache[ckey] = (found, doc["typeName"])
                return found, doc["typeName"]
            if self.settings.create_shell_entity_for_missing_ref:
                return self._create_shell(ctx, tname, uattrs), tname
        raise AtlasBaseException(AtlasErrorCode.REFERENCED_ENTITY_NOT_FOUND, value)

    def _create_shell(self, ctx: MutationContext, tname: str, uattrs: Dict[str, Any]) -> str:
        reg = self.reg
        et = reg.entities[tname]
        guid = str(uuid.uuid4())
        norm = normalize_attributes(reg, et.attributes, uattrs, tname, check_mandatory=False)
        ctx.docs[guid] = {"guid": guid, "typeName": tname, "status": "ACTIVE", "createdBy": ctx.user,
                          "updatedBy": ctx.user, "createTime": ctx.now, "updateTime": ctx.now, "version": 0,
                          "attributes": norm, "classifications": [], "propagatedClassifications": [], "labels": [],
                          "customAttributes": {}, "businessAttributes": {}, "isIncomplete": True, "provenanceType": 0}
        ctx.orig[guid] = None
        ctx.rels_loaded.add(guid)
        ctx.created.append(guid)
        ctx.touched.add(guid)
        for u in et.unique_attributes:
            if norm.get(u) is not None:
                ctx.unique_add[unique_key(tname, u, norm[u])] = {"guid": guid, "typeName": tname, "attribute": u, "ts": ctx.now}
        getattr(ctx, "_batch_types", {})[guid] = tname
        return guid

    def _active_rels(self, ctx: MutationContext, guid: str, rel_name: str, end: Optional[int]) -> List[dict]:
        out = []
        for rid in ctx.rels_by_entity.get(guid, ()):
            r = ctx.rels[rid]
            if r["typeName"] != rel_name or r.get("status") != "ACTIVE":
                continue
            if end is None or r[f"end{end}Guid"] == guid:
                out.append(r)
        return out

    def _new_rel(self, ctx: MutationContext, rt: RelationshipType, end1: str, end2: str,
                 attrs: Optional[dict] = None, index: Optional[int] = None) -> dict:
        r = {
            "guid": str(uuid.uuid4()), "typeName": rt.name, "label": rt.label, "status": "ACTIVE",
            "end1Guid": end1, "end1Type": ctx.docs[end1]["typeName"] if end1 in ctx.docs else rt.end1.type,
            "end2Guid": end2, "end2Type": ctx.docs[end2]["typeName"] if end2 in ctx.docs else rt.end2.type,
            "propagateTags": rt.propagate_tags, "attributes": attrs or {}, "blockedPropagatedClassifications": [],
            "createdBy": ctx.user, "updatedBy": ctx.user, "createTime": ctx.now, "updateTime": ctx.now,
            "version": 0, "provenanceType": 0, "deletedByEntity": False,
        }
        if index is not None:
            r["endIndex"] = index
        ctx.rels[r["guid"]] = r
        ctx.rel_orig[r["guid"]] = None
        for g in (end1, end2):
            ctx.rels_by_entity.setdefault(g, set()).add(r["guid"])
        ctx.rel_changed_entities.update((end1, end2))
        self._collect_pairs(ctx, (end1, end2))
        return r

    def _delete_rel(self, ctx: MutationContext, r: dict, by_entity: bool = False) -> None:
        if r.get("status") != "ACTIVE":
            return
        r["status"] = "DELETED"
        r["deletedByEntity"] = by_entity
        r["updateTime"] = ctx.now
        r["updatedBy"] = ctx.user
        r["version"] = int(r.get("version") or 0) + 1
        ctx.rel_changed_entities.update((r["end1Guid"], r["end2Guid"]))
        self._collect_pairs(ctx, (r["end1Guid"], r["end2Guid"]))

    def _collect_pairs(self, ctx: MutationContext, guids: Iterable[str]) -> None:
        for g in guids:
            ctx.prop_pairs |= pairs_of(ctx.docs.get(g))
            if g not in ctx.docs:
                ctx.__dict__.setdefault("_pair_lookup", set()).add(g)

    def _pick_end(self, ends: List[RelEnd], target_type: str, hint: Optional[str]) -> RelEnd:
        reg = self.reg
        if hint:
            for re_ in ends:
                if re_.rel.name == hint:
                    return re_
            raise AtlasBaseException(AtlasErrorCode.INVALID_RELATIONSHIP_TYPE, hint, target_type)
        tt = reg.entities.get(target_type)
        for re_ in ends:
            if tt is not None and tt.isa(re_.other_type):
                return re_
        e = ends[0]
        raise AtlasBaseException(AtlasErrorCode.INVALID_RELATIONSHIP_END_TYPE, e.rel.name, e.rel.end1.type,
                                 e.rel.end2.type, target_type, e.other_type)

    async def _apply_relationship_attrs(self, ctx: MutationContext, guid: str, rel_values: Dict[str, Any],
                                        is_partial: bool, append_relationships: Optional[bool],
                                        batch_guids: Set[str]) -> None:
        reg = self.reg
        doc = ctx.docs[guid]
        et = reg.entities[doc["typeName"]]
        append_opt = set()
        raw_opt = et.options.get("appendRelationshipsOnPartialUpdate")
        if raw_opt:
            try:
                import json as _json
                append_opt = set(_json.loads(raw_opt))
            except ValueError:
                append_opt = {raw_opt}
        for attr, value in rel_values.items():
            ends = et.relationship_attributes[attr]
            items = [] if value is None else (list(value) if isinstance(value, (list, tuple)) else [value])
            desired: Dict[str, List[Tuple[str, dict, int]]] = {}
            for i, item in enumerate(items):
                if item is None:
                    continue
                hint = item.get("relationshipType") if isinstance(item, dict) else None
                target_guid, target_type = await self._resolve_ref(ctx, item, ends[0].other_type)
                re_ = self._pick_end(ends, target_type, hint)
                rel_attrs = {}
                if isinstance(item, dict) and item.get("relationshipAttributes"):
                    ra = item["relationshipAttributes"]
                    ra_vals = ra.get("attributes") if isinstance(ra, dict) and "attributes" in ra else ra
                    rel_attrs = normalize_attributes(reg, re_.rel.attribute_defs, ra_vals or {}, re_.rel.name,
                                                     check_mandatory=False)
                desired.setdefault(re_.rel.name, []).append((target_guid, rel_attrs, i))
            touched_ends = [re_ for re_ in ends if re_.rel.name in desired] if desired else list(ends)
            append_only = (append_relationships is True) or (is_partial and attr in append_opt)
            for re_ in touched_ends:
                want = desired.get(re_.rel.name, [])
                if re_.cardinality == SINGLE and len(want) > 1:
                    raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE, f"{et.name}.{attr} accepts a single value")
                await self._ensure_rels(ctx, [guid], re_.rel.name)
                if re_.other_cardinality == SINGLE:
                    await self._ensure_rels(ctx, [t for t, _, _ in want], re_.rel.name)
                symmetric = re_.rel.end1.type == re_.rel.end2.type and re_.rel.end1.name == re_.rel.end2.name
                existing = self._active_rels(ctx, guid, re_.rel.name, None if symmetric else re_.end)
                want_guids = {t for t, _, _ in want}
                if not append_only:
                    for r in existing:
                        other = r["end2Guid"] if r["end1Guid"] == guid else r["end1Guid"]
                        if other not in want_guids:
                            self._delete_rel(ctx, r)
                            if re_.owns_other and other not in batch_guids:
                                await self._delete_entities(ctx, [other], cascade_reason="owner")
                for target, rel_attrs, idx in want:
                    match = next((r for r in existing if r.get("status") == "ACTIVE" and
                                  (r["end2Guid"] if r["end1Guid"] == guid else r["end1Guid"]) == target), None)
                    list_index = idx if re_.cardinality == "LIST" else None
                    if match is not None:
                        if rel_attrs and match.get("attributes") != {**(match.get("attributes") or {}), **rel_attrs}:
                            match["attributes"] = {**(match.get("attributes") or {}), **rel_attrs}
                            match["updateTime"] = ctx.now
                            match["version"] = int(match.get("version") or 0) + 1
                        if list_index is not None and match.get("endIndex") != list_index:
                            match["endIndex"] = list_index
                        continue
                    # enforce SINGLE cardinality on the other side (e.g. column.table)
                    if re_.other_cardinality == SINGLE and not symmetric and re_.rel.end(re_.other_end).name:
                        for r in self._active_rels(ctx, target, re_.rel.name, re_.other_end):
                            self._delete_rel(ctx, r)
                    if re_.cardinality == SINGLE:
                        for r in self._active_rels(ctx, guid, re_.rel.name, re_.end):
                            self._delete_rel(ctx, r)
                    if re_.end == 1:
                        self._new_rel(ctx, re_.rel, guid, target, rel_attrs, list_index)
                    else:
                        self._new_rel(ctx, re_.rel, target, guid, rel_attrs, list_index)

    # ------------------------------------------------------------------ delete
    async def delete_by_guids(self, guids: List[str], user: str) -> dict:
        ctx = MutationContext(user=user)
        docs = await self.store.mget(self.store.entities, guids, with_version=True)
        for g in guids:
            if g not in docs:
                raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, g)
            self._verify("entity-delete", docs[g], f"delete entity: guid={g}")
        for g, d in docs.items():
            ctx.docs[g] = d
            ctx.orig[g] = copy.deepcopy(d)
        await self._delete_entities(ctx, guids)
        await self._commit(ctx)
        return self._mutation_response(ctx)

    async def _delete_entities(self, ctx: MutationContext, guids: List[str], cascade_reason: str = "") -> None:
        reg = self.reg
        queue = list(guids)
        while queue:
            g = queue.pop(0)
            doc = await self._ensure_entity(ctx, g)
            if doc.get("status") == "DELETED" or g in ctx.deleted:
                continue
            ctx.prop_pairs |= pairs_of(doc)
            doc["status"] = "DELETED"
            doc["updateTime"] = ctx.now
            doc["updatedBy"] = ctx.user
            doc["version"] = int(doc.get("version") or 0) + 1
            ctx.deleted.append(g)
            ctx.touched.add(g)
            et = reg.entities.get(doc["typeName"])
            for u in (et.unique_attributes if et else []):
                v = (doc.get("attributes") or {}).get(u)
                if v is not None:
                    k = unique_key(doc["typeName"], u, v)
                    ctx.unique_del.add(k)
                    ctx.unique_add.pop(k, None)
            await self._preload_rels(ctx, [g])
            for rid in list(ctx.rels_by_entity.get(g, ())):
                r = ctx.rels[rid]
                if r.get("status") != "ACTIVE":
                    continue
                rt = reg.relationships.get(r["typeName"])
                self._delete_rel(ctx, r, by_entity=True)
                if rt is not None and rt.category == "COMPOSITION":
                    if r["end1Guid"] == g and rt.end1.is_container:
                        queue.append(r["end2Guid"])
                    elif r["end2Guid"] == g and rt.end2.is_container:
                        queue.append(r["end1Guid"])
            ctx.audits.append(audit_event(g, "ENTITY_DELETE", ctx.user, details("Deleted", entity_to_api(
                reg, doc, include_relationships=False)), ctx.now))

    async def purge(self, guids: List[str], user: str) -> dict:
        ctx = MutationContext(user=user)
        docs = await self.store.mget(self.store.entities, guids)
        for g in guids:
            d = docs.get(g)
            if d is None or d.get("status") != "DELETED":
                continue
            ctx.purged.append(g)
            ctx.docs[g] = d
            ctx.audits.append(audit_event(g, "ENTITY_PURGE", user, details("Purged", entity_header(self.reg, d)), ctx.now))
        if ctx.purged:
            for r in await self.rels_of(ctx.purged):
                ctx.purged_rels.add(r["guid"])
            actions = [{"op": "delete", "index": self.store.entities, "id": g} for g in ctx.purged]
            actions += [{"op": "delete", "index": self.store.relationships, "id": rid} for rid in ctx.purged_rels]
            await self.store.bulk(actions)
            await self.audit.write(ctx.audits)
        return self._mutation_response(ctx)

    # ------------------------------------------------------------------ commit
    async def _commit(self, ctx: MutationContext) -> None:
        reg = self.reg
        # pairs for entities that were only referenced (not loaded) by relationship changes
        lookup = getattr(ctx, "_pair_lookup", set()) - set(ctx.docs)
        if lookup:
            for d in (await self.store.mget(self.store.entities, lookup)).values():
                ctx.prop_pairs |= pairs_of(d)
        # 1. unique keys (atomic create; keys that are released and re-taken in this request are overwritten)
        created_keys: List[str] = []
        to_add = dict(ctx.unique_add)
        if to_add:
            res = await self.store.bulk([{"op": "index" if k in ctx.unique_del else "create", "index": self.store.unique,
                                          "id": k, "doc": v} for k, v in to_add.items()])
            conflicts = []
            for r in res:
                if r["status"] in (200, 201):
                    if r["id"] not in ctx.unique_del:
                        created_keys.append(r["id"])
                elif r["status"] == 409:
                    owner = await self.store.get(self.store.unique, r["id"])
                    if owner and owner.get("guid") == to_add[r["id"]]["guid"]:
                        continue
                    if owner and await self._is_stale_unique_owner(owner):
                        await self.store.put(self.store.unique, r["id"], to_add[r["id"]])
                        continue
                    conflicts.append(r["id"])
                else:
                    conflicts.append(r["id"])
            if conflicts:
                await self.store.bulk([{"op": "delete", "index": self.store.unique, "id": k} for k in created_keys])
                info = to_add[conflicts[0]]
                raise AtlasBaseException(AtlasErrorCode.INSTANCE_UNIQUE_ATTRIBUTE_CONFLICT, info["typeName"],
                                         info["attribute"], ctx.docs.get(info["guid"], {}).get("attributes", {}).get(info["attribute"]))

        # 2. entity + relationship documents
        actions: List[dict] = []
        for g in ctx.touched:
            doc = ctx.docs[g]
            seq, term = doc.get("_seq_no"), doc.get("_primary_term")
            clean = strip_internal(doc)
            build_index_fields(reg, clean)
            a = {"op": "index" if ctx.orig.get(g) is not None else "create", "index": self.store.entities, "id": g,
                 "doc": clean}
            if ctx.orig.get(g) is not None and seq is not None:
                a["if_seq_no"], a["if_primary_term"] = seq, term
            actions.append(a)
            ctx.docs[g] = clean
        for rid, r in ctx.rels.items():
            if ctx.rel_orig.get(rid) == r:
                continue
            actions.append({"op": "index", "index": self.store.relationships, "id": rid,
                            "doc": build_relationship_index_fields(reg, r)})
        results = await self.store.bulk(actions)
        failed = [r for r in results if r["status"] not in (200, 201)]
        if failed:
            # roll back unique keys we added; entity docs that did get written stay (best effort)
            await self.store.bulk([{"op": "delete", "index": self.store.unique, "id": k} for k in created_keys])
            f = failed[0]
            if f["status"] == 409:
                raise AtlasBaseException(AtlasErrorCode.CONCURRENT_UPDATE, f["id"])
            raise AtlasBaseException(AtlasErrorCode.INTERNAL_ERROR, f"bulk write failed: {f.get('error')}")

        # 3. release unique keys of deleted / changed values
        stale = [k for k in ctx.unique_del if k not in ctx.unique_add]
        if stale:
            await self.store.bulk([{"op": "delete", "index": self.store.unique, "id": k} for k in stale])

        # 3b. glossary term assignments are denormalised onto the assigned entities ("meanings")
        meaning_targets = {r["end2Guid"] for rid, r in ctx.rels.items()
                           if r["typeName"] == MEANING_REL and ctx.rel_orig.get(rid) != r}
        if meaning_targets:
            await self.refresh_meanings(meaning_targets)

        # 4. audits
        for g in ctx.created:
            ctx.audits.append(audit_event(g, "ENTITY_CREATE", ctx.user,
                                          details("Created", entity_to_api(reg, ctx.docs[g], include_relationships=False)), ctx.now))
        for g in ctx.updated + ctx.partial:
            ctx.audits.append(audit_event(g, "ENTITY_UPDATE", ctx.user,
                                          details("Updated", entity_to_api(reg, ctx.docs[g], include_relationships=False)), ctx.now))

        # 5. propagation
        if ctx.prop_pairs:
            deferred = _deferred_pairs.get()
            if deferred is not None:
                deferred |= ctx.prop_pairs     # bulk operation: recomputed once at the end
            else:
                ctx.audits += await self.propagator.recompute(ctx.prop_pairs, ctx.user)
        await self.audit.write(ctx.audits)

    async def _is_stale_unique_owner(self, owner: dict) -> bool:
        """A unique key whose entity no longer exists or was deleted can be taken over."""
        d = await self.store.get(self.store.entities, owner.get("guid", ""))
        if d is None:
            # the owner may be a concurrent request that has not written its entity yet
            return now_ms() - int(owner.get("ts") or 0) > 60000
        return d.get("status") == "DELETED"

    def _mutation_response(self, ctx: MutationContext) -> dict:
        reg = self.reg
        mutated: Dict[str, List[dict]] = {}

        def hdr(g):
            return entity_header(reg, ctx.docs[g])
        if ctx.created:
            mutated["CREATE"] = [hdr(g) for g in ctx.created]
        if ctx.updated:
            mutated["UPDATE"] = [hdr(g) for g in ctx.updated if g not in ctx.created]
            if not mutated["UPDATE"]:
                del mutated["UPDATE"]
        if ctx.partial:
            mutated["PARTIAL_UPDATE"] = [hdr(g) for g in ctx.partial if g not in ctx.created]
            if not mutated["PARTIAL_UPDATE"]:
                del mutated["PARTIAL_UPDATE"]
        if ctx.deleted:
            mutated["DELETE"] = [hdr(g) for g in ctx.deleted]
        if ctx.purged:
            mutated["PURGE"] = [hdr(g) for g in ctx.purged]
        out: Dict[str, Any] = {}
        if mutated:
            out["mutatedEntities"] = mutated
        if ctx.guid_assignments:
            out["guidAssignments"] = ctx.guid_assignments
        return out

    # ------------------------------------------------------------------ partial updates
    async def update_attribute_by_guid(self, guid: str, attr_name: str, value: Any, user: str) -> dict:
        doc = await self._get_doc(guid)
        self._verify("entity-update", doc, f"update entity ByUniqueAttributes : guid={guid}")
        et = self.reg.entity_type(doc["typeName"])
        if attr_name not in et.attributes and attr_name not in et.relationship_attributes:
            raise AtlasBaseException(AtlasErrorCode.INVALID_PARTIAL_UPDATE_ATTR, attr_name, doc["typeName"])
        entity = {"guid": guid, "typeName": doc["typeName"], "attributes": {attr_name: value}}
        return await self.create_or_update({"entity": entity}, user, is_partial=False)

    async def update_by_unique_attributes(self, type_name: str, uattrs: Dict[str, Any], payload: dict, user: str) -> dict:
        guid = await self.get_guid_by_unique_attributes(type_name, uattrs)
        entity = copy.deepcopy(payload.get("entity") or {})
        entity["guid"] = guid
        entity.setdefault("typeName", type_name)
        doc = await self._get_doc(guid)
        entity["typeName"] = doc["typeName"]
        return await self.create_or_update({"entity": entity, "referredEntities": payload.get("referredEntities") or {}},
                                           user, is_partial=True)

    # ------------------------------------------------------------------ classifications
    def _normalize_classification(self, doc: dict, c: dict) -> dict:
        reg = self.reg
        tname = c.get("typeName")
        ct = reg.classifications.get(tname)
        if ct is None:
            raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_NOT_FOUND, tname)
        if ct.entity_types is not None and doc["typeName"] not in ct.entity_types:
            raise AtlasBaseException(AtlasErrorCode.INVALID_ENTITY_FOR_CLASSIFICATION, doc["guid"], doc["typeName"], tname)
        attrs = normalize_struct(reg, tname, {"attributes": c.get("attributes") or {}}, tname)["attributes"]
        for a in ct.attributes.values():
            if not a.is_optional and attrs.get(a.name) is None:
                dv = default_for(reg, a)
                if dv is None:
                    raise AtlasBaseException(AtlasErrorCode.MISSING_MANDATORY_ATTRIBUTE, tname, a.name)
                attrs[a.name] = dv
        out = {"typeName": tname, "attributes": attrs, "entityGuid": doc["guid"],
               "propagate": True if c.get("propagate") is None else bool(c["propagate"]),
               "removePropagationsOnEntityDelete": bool(c.get("removePropagationsOnEntityDelete", False))}
        if c.get("validityPeriods"):
            out["validityPeriods"] = c["validityPeriods"]
        return out

    def _set_classifications(self, ctx: MutationContext, doc: dict, classifications: List[dict]) -> None:
        new = []
        seen = set()
        for c in classifications:
            nc = self._normalize_classification(doc, c)
            if nc["typeName"] in seen:
                continue
            seen.add(nc["typeName"])
            new.append(nc)
        old = {c["typeName"]: c for c in doc.get("classifications") or []}
        newd = {c["typeName"]: c for c in new}
        for n in set(old) | set(newd):
            if old.get(n) != newd.get(n):
                ctx.prop_pairs.add((doc["guid"], n))
                if n not in old:
                    ctx.audits.append(audit_event(doc["guid"], "CLASSIFICATION_ADD", ctx.user,
                                                  details("Added classification", classification_to_api(newd[n], doc["guid"], doc.get("status", "ACTIVE"))), ctx.now))
                elif n not in newd:
                    ctx.audits.append(audit_event(doc["guid"], "CLASSIFICATION_DELETE", ctx.user,
                                                  details("Deleted classification", n), ctx.now))
                else:
                    ctx.audits.append(audit_event(doc["guid"], "CLASSIFICATION_UPDATE", ctx.user,
                                                  details("Updated classification", classification_to_api(newd[n], doc["guid"], doc.get("status", "ACTIVE"))), ctx.now))
        doc["classifications"] = new

    async def _single_entity_ctx(self, guid: str, user: str) -> Tuple[MutationContext, dict]:
        ctx = MutationContext(user=user)
        doc = await self.store.get(self.store.entities, guid, with_version=True)
        if doc is None:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, guid)
        ctx.docs[guid] = doc
        ctx.orig[guid] = copy.deepcopy(doc)
        return ctx, doc

    async def _finish_single(self, ctx: MutationContext, guid: str) -> None:
        self._finalize_entity(ctx, guid, is_partial=False)
        if guid in ctx.updated:
            ctx.touched.add(guid)
            ctx.updated.remove(guid)   # classification/label changes are not reported as ENTITY_UPDATE audits
        await self._commit(ctx)

    async def add_classifications(self, guid: str, classifications: List[dict], user: str) -> None:
        ctx, doc = await self._single_entity_ctx(guid, user)
        for c in classifications:
            self._verify("entity-add-classification", doc,
                         f"add classification: guid={guid}, classification={c.get('typeName')}",
                         classification=c.get("typeName"))
        cur = list(doc.get("classifications") or [])
        names = {c["typeName"] for c in cur}
        for c in classifications:
            if c.get("typeName") in names:
                raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_ALREADY_ASSOCIATED, guid, c.get("typeName"))
            cur.append(c)
            names.add(c.get("typeName"))
        self._set_classifications(ctx, doc, cur)
        await self._finish_single(ctx, guid)

    async def update_classifications(self, guid: str, classifications: List[dict], user: str) -> None:
        ctx, doc = await self._single_entity_ctx(guid, user)
        for c in classifications:
            self._verify("entity-update-classification", doc,
                         f"update classification: guid={guid}, classification={c.get('typeName')}",
                         classification=c.get("typeName"))
        cur = {c["typeName"]: c for c in doc.get("classifications") or []}
        prop = {c["typeName"] for c in doc.get("propagatedClassifications") or []}
        for c in classifications:
            n = c.get("typeName")
            if n not in cur:
                if n in prop:
                    raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_UPDATE_FROM_PROPAGATED_ENTITY, n)
                raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_NOT_FOUND, n)
            merged = dict(cur[n])
            merged["attributes"] = {**(cur[n].get("attributes") or {}), **(c.get("attributes") or {})}
            for k in ("propagate", "removePropagationsOnEntityDelete", "validityPeriods"):
                if c.get(k) is not None:
                    merged[k] = c[k]
            cur[n] = merged
        self._set_classifications(ctx, doc, list(cur.values()))
        await self._finish_single(ctx, guid)

    async def delete_classification(self, guid: str, name: str, user: str, associated_guid: Optional[str] = None) -> None:
        if associated_guid and associated_guid != guid:
            raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_DELETE_FROM_PROPAGATED_ENTITY, name)
        ctx, doc = await self._single_entity_ctx(guid, user)
        self._verify("entity-remove-classification", doc, f"remove classification: guid={guid}, classification={name}",
                     classification=name)
        cur = [c for c in doc.get("classifications") or []]
        if not any(c["typeName"] == name for c in cur):
            if any(c["typeName"] == name for c in doc.get("propagatedClassifications") or []):
                raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_DELETE_FROM_PROPAGATED_ENTITY, name)
            raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_NOT_FOUND, name)
        self._set_classifications(ctx, doc, [c for c in cur if c["typeName"] != name])
        await self._finish_single(ctx, guid)

    async def set_classifications(self, guid_header_map: Dict[str, dict], user: str) -> None:
        for guid, header in guid_header_map.items():
            ctx, doc = await self._single_entity_ctx(guid, user)
            direct = [c for c in header.get("classifications") or [] if c.get("entityGuid") in (None, guid)]
            old = {c["typeName"]: c for c in doc.get("classifications") or []}
            new = {c.get("typeName") for c in direct}
            for c in direct:
                n = c.get("typeName")
                priv = "entity-update-classification" if n in old else "entity-add-classification"
                self._verify(priv, doc, f"{priv.split('-')[1]} classification: guid={guid}, classification={n}",
                             classification=n)
            for n in set(old) - new:
                self._verify("entity-remove-classification", doc,
                             f"remove classification: guid={guid}, classification={n}", classification=n)
            self._set_classifications(ctx, doc, direct)
            await self._finish_single(ctx, guid)

    async def get_classifications(self, guid: str) -> List[dict]:
        doc = await self._get_doc(guid)
        self._verify("entity-read", doc, f"get classifications: guid={guid}")
        return entity_header(self.reg, doc)["classifications"]

    # ------------------------------------------------------------------ labels
    def _validate_labels(self, labels: Iterable[str]) -> List[str]:
        out = []
        for lbl in labels or []:
            lbl = str(lbl).strip()
            if not lbl:
                continue
            if not LABEL_RE.match(lbl) or len(lbl) > 50:
                raise AtlasBaseException(AtlasErrorCode.INVALID_LABEL_CHARACTERS, lbl)
            if lbl not in out:
                out.append(lbl)
        return out

    async def modify_labels(self, guid: str, labels: Iterable[str], mode: str, user: str) -> None:
        ctx, doc = await self._single_entity_ctx(guid, user)
        new = self._validate_labels(labels)
        cur = list(doc.get("labels") or [])
        if mode == "set":
            result = new
        elif mode == "add":
            result = cur + [x for x in new if x not in cur]
        else:
            result = [x for x in cur if x not in new]
        added = [x for x in result if x not in cur]
        removed = [x for x in cur if x not in result]
        for lbl in added:
            self._verify("entity-add-label", doc, f"add label: guid={guid}, label={lbl}", label=lbl)
        for lbl in removed:
            self._verify("entity-remove-label", doc, f"remove label: guid={guid}, label={lbl}", label=lbl)
        doc["labels"] = result
        if added:
            ctx.audits.append(audit_event(guid, "LABEL_ADD", user, details("Added labels", added), ctx.now))
        if removed:
            ctx.audits.append(audit_event(guid, "LABEL_DELETE", user, details("Deleted labels", removed), ctx.now))
        ctx.touched.add(guid)
        await self._finish_single(ctx, guid)

    # ------------------------------------------------------------------ custom / business attributes
    def _validate_custom_attributes(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        out = {}
        for k, v in (attrs or {}).items():
            if len(k) > 50:
                raise AtlasBaseException(AtlasErrorCode.INVALID_CUSTOM_ATTRIBUTE_KEY_LENGTH, k)
            out[str(k)] = "" if v is None else str(v)
        return out

    def _validate_business_attributes(self, type_name: str, bm_attrs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        reg = self.reg
        out: Dict[str, Dict[str, Any]] = {}
        for bm_name, attrs in (bm_attrs or {}).items():
            bmt = reg.business_metadata.get(bm_name)
            if bmt is None:
                raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, bm_name)
            vals = {}
            for an, v in (attrs or {}).items():
                a = bmt.attributes.get(an)
                if a is None:
                    raise AtlasBaseException(AtlasErrorCode.UNKNOWN_ATTRIBUTE, an, bm_name)
                allowed = bmt.applicable.get(an)
                if allowed is not None and type_name not in allowed:
                    raise AtlasBaseException(AtlasErrorCode.BUSINESS_METADATA_NOT_ALLOWED, f"{bm_name}.{an}", type_name)
                nv = normalize_value(reg, a.type_name, v, f"{bm_name}.{an}")
                ml = bmt.max_len.get(an)
                if ml and isinstance(nv, str) and len(nv) > ml:
                    raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE, f"{bm_name}.{an} exceeds maxStrLength {ml}")
                vals[an] = nv
            out[bm_name] = vals
        return out

    async def add_or_update_business_attributes(self, guid: str, bm_attrs: Dict[str, Dict[str, Any]], overwrite: bool,
                                                user: str) -> None:
        ctx, doc = await self._single_entity_ctx(guid, user)
        for bm in (bm_attrs or {}):
            self._verify("entity-update-business-metadata", doc,
                         f"add/update business-metadata: guid={guid}, business-metadata-name={bm}", bm=bm)
        new = self._validate_business_attributes(doc["typeName"], bm_attrs)
        if overwrite:
            doc["businessAttributes"] = new
        else:
            cur = copy.deepcopy(doc.get("businessAttributes") or {})
            for k, v in new.items():
                cur.setdefault(k, {}).update(v)
            doc["businessAttributes"] = cur
        ctx.audits.append(audit_event(guid, "BUSINESS_ATTRIBUTE_UPDATE", user, details("Updated business attributes", new), ctx.now))
        ctx.touched.add(guid)
        await self._finish_single(ctx, guid)

    async def remove_business_attributes(self, guid: str, bm_attrs: Dict[str, Dict[str, Any]], user: str) -> None:
        ctx, doc = await self._single_entity_ctx(guid, user)
        for bm in (bm_attrs or {}):
            self._verify("entity-update-business-metadata", doc,
                         f"remove business-metadata: guid={guid}, business-metadata={bm}", bm=bm)
        cur = copy.deepcopy(doc.get("businessAttributes") or {})
        for bm, attrs in (bm_attrs or {}).items():
            if bm not in cur:
                continue
            if not attrs:
                cur.pop(bm)
                continue
            for an in attrs:
                cur[bm].pop(an, None)
            if not cur[bm]:
                cur.pop(bm)
        doc["businessAttributes"] = cur
        ctx.audits.append(audit_event(guid, "BUSINESS_ATTRIBUTE_UPDATE", user, details("Removed business attributes", bm_attrs), ctx.now))
        ctx.touched.add(guid)
        await self._finish_single(ctx, guid)

    async def import_business_metadata(self, rows: List[List[str]], user: str) -> dict:
        """Atlas bulkCreateOrUpdateBusinessAttributes: EntityType, UniqueAttrValue, BM.attr, value[, UniqueAttrName]."""
        reg = self.reg
        failed, success = [], []
        per_entity: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for n, r in enumerate(rows, start=1):
            r = [(c or "").strip() for c in r] + [""] * 5
            type_name, uval, bm_attr, value, uname = r[0], r[1], r[2], r[3], r[4] or "qualifiedName"
            try:
                et = reg.entities.get(type_name)
                if et is None:
                    raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, type_name)
                if "." not in bm_attr:
                    raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST,
                                             f"Invalid business attribute name {bm_attr}; expected <businessMetadata>.<attribute>")
                bm, an = bm_attr.split(".", 1)
                bmt = reg.business_metadata.get(bm)
                if bmt is None or an not in bmt.attributes:
                    raise AtlasBaseException(AtlasErrorCode.UNKNOWN_ATTRIBUTE, bm_attr, type_name)
                guid = await self.find_guid_by_unique_attributes(type_name, {uname: uval})
                if guid is None:
                    raise AtlasBaseException(AtlasErrorCode.INSTANCE_BY_UNIQUE_ATTRIBUTE_NOT_FOUND, type_name, uval)
                a = bmt.attributes[an]
                v: Any = value.split("|") if a.kind == "array" else value
                per_entity.setdefault(guid, {}).setdefault(bm, {})[an] = v
            except AtlasBaseException as e:
                failed.append({"parentObjectName": type_name, "childObjectName": uval, "importStatus": "FAILED",
                               "remarks": e.message, "rowNumber": n})
        for guid, bm_attrs in per_entity.items():
            try:
                await self.add_or_update_business_attributes(guid, bm_attrs, True, user)
                success.append({"parentObjectName": guid, "childObjectName": str(bm_attrs), "importStatus": "SUCCESS"})
            except AtlasBaseException as e:
                failed.append({"parentObjectName": guid, "childObjectName": str(bm_attrs), "importStatus": "FAILED",
                               "remarks": e.message})
        return {"failedImportInfoList": failed, "successImportInfoList": success}

    # ================================================================== relationships (RelationshipREST)
    async def get_relationship(self, guid: str, extended_info: bool = False) -> dict:
        r = await self.store.get(self.store.relationships, guid)
        if r is None:
            raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_GUID_NOT_FOUND, guid)
        ends = await self.store.mget(self.store.entities, [r["end1Guid"], r["end2Guid"]])
        for end in ("end1Guid", "end2Guid"):
            if ends.get(r[end]) is not None:
                self._verify("entity-read", ends[r[end]], f"read relationship: guid={guid}")
        rel = relationship_to_api(self.reg, r, ends.get(r["end1Guid"]), ends.get(r["end2Guid"]))
        if extended_info:
            referred = {g: entity_header(self.reg, d) for g, d in ends.items()}
            return {"relationship": rel, "referredEntities": referred}
        return {"relationship": rel}

    async def _resolve_end(self, end: Optional[dict], expected_type: str) -> dict:
        if not end:
            raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_END_IS_NULL, expected_type)
        guid = end.get("guid")
        if is_assigned_guid(guid):
            return await self._get_doc(guid)
        if end.get("uniqueAttributes"):
            g = await self.get_guid_by_unique_attributes(end.get("typeName") or expected_type, end["uniqueAttributes"])
            return await self._get_doc(g)
        raise AtlasBaseException(AtlasErrorCode.INVALID_OBJECT_ID, end)

    async def create_relationship(self, rel: dict, user: str) -> dict:
        reg = self.reg
        rt = reg.relationships.get(rel.get("typeName") or "")
        if rt is None or rt.synthetic:
            raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, rel.get("typeName"))
        e1 = await self._resolve_end(rel.get("end1"), rt.end1.type)
        e2 = await self._resolve_end(rel.get("end2"), rt.end2.type)
        if not reg.entities[e1["typeName"]].isa(rt.end1.type) or not reg.entities[e2["typeName"]].isa(rt.end2.type):
            raise AtlasBaseException(AtlasErrorCode.INVALID_RELATIONSHIP_END_TYPE, rt.name, e1["typeName"], e2["typeName"],
                                     rt.end1.type, rt.end2.type)
        self._verify_rel("add-relationship", rt.name, e1, e2)
        ctx = MutationContext(user=user)
        for d in (e1, e2):
            ctx.docs[d["guid"]] = d
            ctx.orig[d["guid"]] = copy.deepcopy(d)
        await self._ensure_rels(ctx, [e1["guid"], e2["guid"]], rt.name)
        for r in self._active_rels(ctx, e1["guid"], rt.name, 1):
            if r["end2Guid"] == e2["guid"]:
                raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_ALREADY_EXISTS, rt.name, e1["guid"], e2["guid"])
        if rt.end1.cardinality == SINGLE:
            for r in self._active_rels(ctx, e1["guid"], rt.name, 1):
                self._delete_rel(ctx, r)
        if rt.end2.cardinality == SINGLE:
            for r in self._active_rels(ctx, e2["guid"], rt.name, 2):
                self._delete_rel(ctx, r)
        attrs = normalize_attributes(reg, rt.attribute_defs, rel.get("attributes") or {}, rt.name, check_mandatory=True)
        r = self._new_rel(ctx, rt, e1["guid"], e2["guid"], attrs)
        if rel.get("propagateTags"):
            r["propagateTags"] = rel["propagateTags"]
        if rel.get("blockedPropagatedClassifications"):
            r["blockedPropagatedClassifications"] = rel["blockedPropagatedClassifications"]
        await self._commit(ctx)
        return relationship_to_api(reg, r, e1, e2)

    async def update_relationship(self, rel: dict, user: str) -> dict:
        reg = self.reg
        guid = rel.get("guid")
        r = await self.store.get(self.store.relationships, guid) if guid else None
        if r is None:
            raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_GUID_NOT_FOUND, guid)
        rt = reg.relationship_type(r["typeName"])
        await self._verify_rel_by_ends("update-relationship", r)
        ctx = MutationContext(user=user)
        ctx.rels[guid] = r
        ctx.rel_orig[guid] = copy.deepcopy(r)
        if rel.get("attributes") is not None:
            r["attributes"] = {**(r.get("attributes") or {}),
                               **normalize_attributes(reg, rt.attribute_defs, rel["attributes"], rt.name, False)}
        if rel.get("propagateTags"):
            r["propagateTags"] = rel["propagateTags"]
        if rel.get("blockedPropagatedClassifications") is not None:
            r["blockedPropagatedClassifications"] = rel["blockedPropagatedClassifications"]
        if ctx.rel_orig[guid] != r:
            r["updateTime"] = ctx.now
            r["updatedBy"] = user
            r["version"] = int(r.get("version") or 0) + 1
            self._collect_pairs(ctx, (r["end1Guid"], r["end2Guid"]))
        await self._commit(ctx)
        ends = await self.store.mget(self.store.entities, [r["end1Guid"], r["end2Guid"]])
        return relationship_to_api(reg, r, ends.get(r["end1Guid"]), ends.get(r["end2Guid"]))

    async def delete_relationship(self, guid: str, user: str) -> None:
        r = await self.store.get(self.store.relationships, guid)
        if r is None:
            raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_GUID_NOT_FOUND, guid)
        if r.get("status") == "DELETED":
            return
        await self._verify_rel_by_ends("remove-relationship", r)
        ctx = MutationContext(user=user)
        ctx.rels[guid] = r
        ctx.rel_orig[guid] = copy.deepcopy(r)
        self._delete_rel(ctx, r)
        await self._commit(ctx)

    def _verify_rel(self, privilege: str, rel_type: str, e1: Optional[dict], e2: Optional[dict]) -> None:
        if self.authz is not None:
            self.authz.verify_relationship(privilege, rel_type, self.authz_header(e1) if e1 else None,
                                           self.authz_header(e2) if e2 else None,
                                           f"{privilege}: type={rel_type}")

    async def _verify_rel_by_ends(self, privilege: str, r: dict) -> None:
        if self.authz is None or not self.authz.enabled:
            return
        ends = await self.store.mget(self.store.entities, [r["end1Guid"], r["end2Guid"]])
        self._verify_rel(privilege, r["typeName"], ends.get(r["end1Guid"]), ends.get(r["end2Guid"]))

    # ================================================================== glossary term assignments
    async def refresh_meanings(self, guids: Iterable[str]) -> None:
        """Recompute the ``meanings`` of entities from their active AtlasGlossarySemanticAssignment relationships."""
        guids = list(dict.fromkeys(guids))
        for _ in range(3):
            docs = await self.store.mget(self.store.entities, guids, with_version=True)
            rels = [r for r in await self.rels_of(list(docs), active_only=True)
                    if r["typeName"] == MEANING_REL and r["end2Guid"] in docs]
            terms = await self.store.mget(self.store.entities, {r["end1Guid"] for r in rels})
            by_entity: Dict[str, List[dict]] = {}
            for r in rels:
                t = terms.get(r["end1Guid"])
                if t is None or t.get("status") == "DELETED":
                    continue
                a = r.get("attributes") or {}
                ta = t.get("attributes") or {}
                m = {"termGuid": t["guid"], "relationGuid": r["guid"], "displayText": ta.get("name"),
                     "qualifiedName": ta.get("qualifiedName")}
                for k in ("description", "expression", "createdBy", "steward", "source", "confidence", "status"):
                    if a.get(k) is not None:
                        m[k] = a[k]
                by_entity.setdefault(r["end2Guid"], []).append(m)
            actions = []
            for g, doc in docs.items():
                meanings = sorted(by_entity.get(g, []), key=lambda m: (m.get("displayText") or "", m["termGuid"]))
                if meanings == (doc.get("meanings") or []):
                    continue
                seq, term = doc.get("_seq_no"), doc.get("_primary_term")
                doc = strip_internal(doc)
                doc["meanings"] = meanings
                doc["meaningNames"] = [m["displayText"] for m in meanings if m.get("displayText")]
                doc["meaningQualifiedNames"] = [m["qualifiedName"] for m in meanings if m.get("qualifiedName")]
                build_index_fields(self.reg, doc)
                actions.append({"op": "index", "index": self.store.entities, "id": g, "doc": doc,
                                "if_seq_no": seq, "if_primary_term": term})
            results = await self.store.bulk(actions)
            guids = [r["id"] for r in results if r["status"] == 409]
            if not guids:
                return

    # ================================================================== misc
    async def audit_events(self, guid: str, **kw) -> List[dict]:
        doc = await self.store.get(self.store.entities, guid)
        if doc is not None:
            self._verify("entity-read", doc, f"read entity audit: guid={guid}")
        return await self.audit.list_events(guid, **kw)

    async def headers_updated_since(self, ts: int) -> Dict[str, dict]:
        q = {"range": {"updateTime": {"gte": ts}}}
        out = {}
        async for g, d in self.store.scan(self.store.entities, q):
            if self.can_read(d):
                out[g] = entity_header(self.reg, d)
        return out

    async def entity_count(self, type_name: str) -> int:
        return await self.store.count(self.store.entities, {"term": {"typeName": type_name}})
