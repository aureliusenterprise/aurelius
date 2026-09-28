"""Discovery services (Atlas ``DiscoveryREST``): basic, quick, full-text, attribute, relationship and saved searches."""
from __future__ import annotations

import copy
import fnmatch
import logging
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Set

from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import SYSTEM_ATTR_FIELDS, entity_header, object_id, relationship_to_api
from ..store.es import EsStore
from ..typesystem.registry import ALL_CLASSIFICATION_TYPES, ALL_ENTITY_TYPES, SINGLE, TypeRegistry
from .filters import criteria_query, resolve_field

log = logging.getLogger(__name__)

CLASSIFIED = "_CLASSIFIED"
NOT_CLASSIFIED = "_NOT_CLASSIFIED"
WILDCARD_CLASSIFICATIONS = "*"


def _bool(v: Any, default: bool) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    return str(v).lower() == "true"


def _int(v: Any, default: int) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


class SearchService:
    def __init__(self, store: EsStore, typedefs, entity_store, settings):
        self.store = store
        self.typedefs = typedefs
        self.entities = entity_store
        self.settings = settings

    @property
    def reg(self) -> TypeRegistry:
        return self.typedefs.registry

    # ------------------------------------------------------------------ helpers
    def _type_set(self, type_name: Optional[str], include_sub_types: bool) -> Optional[List[str]]:
        reg = self.reg
        if not type_name or type_name == ALL_ENTITY_TYPES:
            return None
        out: Set[str] = set()
        for t in [x.strip() for x in type_name.split(",") if x.strip()]:
            if t == ALL_ENTITY_TYPES:
                return None
            et = reg.entities.get(t)
            if et is None:
                raise AtlasBaseException(AtlasErrorCode.UNKNOWN_TYPENAME, t)
            out |= et.type_and_all_sub_types() if include_sub_types else {t}
        return sorted(out)

    def _classification_set(self, name: str, include_sub: bool) -> List[str]:
        reg = self.reg
        names: Set[str] = set()
        for c in [x.strip() for x in name.split(",") if x.strip()]:
            if "*" in c or "?" in c:
                matched = [n for n in reg.classifications if fnmatch.fnmatchcase(n.lower(), c.lower())]
            else:
                if c not in reg.classifications:
                    raise AtlasBaseException(AtlasErrorCode.UNKNOWN_CLASSIFICATION, c)
                matched = [c]
            for m in matched:
                names |= reg.classifications[m].type_and_all_sub_types() if include_sub else {m}
        return sorted(names)

    def text_query(self, text: str) -> dict:
        fields = ["displayText.text^10", "fulltext"]
        for attr, w in sorted(self.reg.search_weights.items()):
            fields.append(f"idx.str.{attr}.text^{w}")
        return {"simple_query_string": {"query": text, "fields": fields, "default_operator": "and",
                                        "analyze_wildcard": True, "lenient": True}}

    def _sort(self, sort_by: Optional[str], sort_order: Optional[str], type_names: List[str], has_query: bool) -> list:
        order = "desc" if str(sort_order or "").upper().startswith("DESC") else "asc"
        if sort_by:
            if sort_by in SYSTEM_ATTR_FIELDS:
                field = SYSTEM_ATTR_FIELDS[sort_by][0]
            elif sort_by in ("name", "displayText") and not type_names:
                field = "displayText.lc"
            else:
                try:
                    ref = resolve_field(self.reg, sort_by, type_names)
                    field = ref.field + (".lc" if ref.has_lc else "")
                except AtlasBaseException:
                    field = "displayText.lc"
            return [{field: {"order": order, "unmapped_type": "keyword", "missing": "_last"}}, {"guid": "asc"}]
        if has_query:
            return ["_score", {"guid": "asc"}]
        return [{"displayText.lc": {"order": "asc", "unmapped_type": "keyword", "missing": "_last"}}, {"guid": "asc"}]

    async def _relationship_values(self, docs: List[dict], attrs: List[str]) -> Dict[str, Dict[str, Any]]:
        """Values of requested relationship attributes for search result headers."""
        reg = self.reg
        wanted: Dict[str, Dict[str, list]] = {}
        need = False
        for d in docs:
            et = reg.entities.get(d["typeName"])
            if et and any(a in et.relationship_attributes and a not in et.attributes or
                          (a in et.attributes and et.attributes[a].is_object_ref) for a in attrs):
                need = True
                break
        if not need:
            return {}
        rels = await self.entities.rels_of([d["guid"] for d in docs], active_only=True)
        others_ids = {r["end1Guid"] for r in rels} | {r["end2Guid"] for r in rels}
        others = await self.store.mget(self.store.entities, others_ids)
        out: Dict[str, Dict[str, Any]] = {}
        by_guid = {d["guid"]: d for d in docs}
        for r in rels:
            rt = reg.relationships.get(r["typeName"])
            if rt is None:
                continue
            for n in (1, 2):
                g = r[f"end{n}Guid"]
                if g not in by_guid:
                    continue
                end = rt.end(n)
                if end.name not in attrs:
                    continue
                other = others.get(r[f"end{2 if n == 1 else 1}Guid"])
                if other is None:
                    continue
                oid = object_id(reg, other)
                oid["displayText"] = other.get("displayText")
                if end.cardinality == SINGLE:
                    out.setdefault(g, {})[end.name] = oid
                else:
                    out.setdefault(g, {}).setdefault(end.name, []).append(oid)
        return out

    async def _headers(self, docs: List[dict], attrs: List[str], include_classification_attrs: bool = True) -> List[dict]:
        rel_values = await self._relationship_values(docs, attrs) if attrs else {}
        out = []
        for d in docs:
            h = entity_header(self.reg, d, attrs, rel_values.get(d["guid"]))
            if not include_classification_attrs:
                h["classifications"] = [{"typeName": c["typeName"], "entityGuid": c.get("entityGuid"),
                                         "entityStatus": c.get("entityStatus")} for c in h["classifications"]]
            out.append(h)
        return out

    # ------------------------------------------------------------------ basic search
    def build_basic_query(self, p: Dict[str, Any]) -> dict:
        reg = self.reg
        include_sub = _bool(p.get("includeSubTypes"), True)
        type_names = self._type_set(p.get("typeName"), include_sub)
        filters: List[dict] = []
        must_not: List[dict] = []
        must: List[dict] = []
        if type_names is not None:
            filters.append({"terms": {"typeName": type_names}})
        else:
            must_not.append({"prefix": {"typeName": "__"}})
            if self.reg.internal_types:
                must_not.append({"terms": {"typeName": self.reg.internal_types}})
        cls = p.get("classification")
        tag_filters = p.get("tagFilters")
        if cls:
            if cls == CLASSIFIED or cls == ALL_CLASSIFICATION_TYPES or cls == WILDCARD_CLASSIFICATIONS:
                filters.append({"exists": {"field": "allClassificationNames"}})
                cls_names = None
            elif cls == NOT_CLASSIFIED:
                must_not.append({"exists": {"field": "allClassificationNames"}})
                cls_names = None
            else:
                cls_names = self._classification_set(cls, _bool(p.get("includeSubClassifications"), True))
                filters.append({"terms": {"allClassificationNames": cls_names}})
            if tag_filters and cls != NOT_CLASSIFIED:
                inner = [criteria_query(reg, tag_filters, cls_names or [], scope="classification")]
                if cls_names:
                    inner.append({"terms": {"tags.typeName": cls_names}})
                filters.append({"nested": {"path": "tags", "query": {"bool": {"filter": [q for q in inner if q]}}}})
        if p.get("termName"):
            t = p["termName"]
            filters.append({"bool": {"should": [{"term": {"meaningQualifiedNames": t}}, {"term": {"meaningNames": t}}],
                                     "minimum_should_match": 1}})
        ef = criteria_query(reg, p.get("entityFilters"), type_names or ([p["typeName"]] if p.get("typeName") else []))
        if ef:
            filters.append(ef)
        if p.get("query"):
            must.append(self.text_query(str(p["query"])))
        if _bool(p.get("excludeDeletedEntities"), False):
            filters.append({"term": {"status": "ACTIVE"}})
        return {"bool": {"filter": filters, "must": must, "must_not": must_not}}, type_names

    async def basic(self, p: Dict[str, Any], query_type: str = "BASIC") -> dict:
        if not any(p.get(k) for k in ("typeName", "classification", "termName", "query")):
            raise AtlasBaseException(AtlasErrorCode.INVALID_SEARCH_PARAMS)
        limit = max(0, min(_int(p.get("limit"), self.settings.search_default_limit), self.settings.search_max_limit))
        offset = max(0, _int(p.get("offset"), 0))
        q, type_names = self.build_basic_query(p)
        sort = self._sort(p.get("sortBy"), p.get("sortOrder"), type_names or [], bool(p.get("query")))
        r = await self.store.search(self.store.entities, q, size=limit, from_=offset, sort=sort)
        docs = [h["_source"] for h in r["hits"]["hits"]]
        attrs = list(p.get("attributes") or [])
        result: Dict[str, Any] = {"queryType": query_type, "searchParameters": p,
                                  "approximateCount": r["hits"]["total"]["value"]}
        if p.get("query"):
            result["queryText"] = p["query"]
        if p.get("typeName"):
            result["type"] = p["typeName"]
        if p.get("classification"):
            result["classification"] = p["classification"]
        if docs:
            result["entities"] = await self._headers(docs, attrs, _bool(p.get("includeClassificationAttributes"), True))
        return result

    # ------------------------------------------------------------------ quick search & suggestions
    async def quick(self, p: Dict[str, Any]) -> dict:
        params = {
            "query": p.get("query"), "typeName": p.get("typeName"), "entityFilters": p.get("entityFilters"),
            "includeSubTypes": _bool(p.get("includeSubTypesOrNot", p.get("includeSubTypes")), True),
            "excludeDeletedEntities": _bool(p.get("excludeDeletedEntities"), True),
            "limit": p.get("limit", 25), "offset": p.get("offset", 0), "attributes": p.get("attributes"),
            "sortBy": p.get("sortBy"), "sortOrder": p.get("sortOrder"),
        }
        params = {k: v for k, v in params.items() if v is not None}
        if not params.get("query") and not params.get("typeName"):
            params["typeName"] = ALL_ENTITY_TYPES
        q, type_names = self.build_basic_query(params)
        limit = max(0, min(_int(params.get("limit"), 25), self.settings.search_max_limit))
        offset = max(0, _int(params.get("offset"), 0))
        sort = self._sort(params.get("sortBy"), params.get("sortOrder"), type_names or [], bool(params.get("query")))
        r = await self.store.search(self.store.entities, q, size=limit, from_=offset, sort=sort,
                                    aggs={"__typeName": {"terms": {"field": "typeName", "size": 100}}})
        docs = [h["_source"] for h in r["hits"]["hits"]]
        res: Dict[str, Any] = {"queryType": "BASIC", "searchParameters": params,
                               "approximateCount": r["hits"]["total"]["value"]}
        if params.get("query"):
            res["queryText"] = params["query"]
        if docs:
            res["entities"] = await self._headers(docs, list(params.get("attributes") or []))
        buckets = (r.get("aggregations") or {}).get("__typeName", {}).get("buckets", [])
        return {"searchResults": res,
                "aggregationMetrics": {"__typeName": [{"name": b["key"], "count": b["doc_count"]} for b in buckets]}}

    async def suggestions(self, prefix: str, field_name: Optional[str] = None) -> dict:
        if not prefix:
            return {"suggestions": []}
        if field_name:
            try:
                ref = resolve_field(self.reg, field_name, [])
                field = ref.field + (".lc" if ref.has_lc else "")
            except AtlasBaseException:
                field = "displayText.lc"
        else:
            field = "displayText.lc"
        q = {"bool": {"filter": [{"prefix": {field: {"value": prefix.lower(), "case_insensitive": True}}},
                                 {"term": {"status": "ACTIVE"}}],
                      "must_not": [{"prefix": {"typeName": "__"}}]}}
        r = await self.store.search(self.store.entities, q, size=50, source=["displayText", "attributes"])
        out: List[str] = []
        src_field = field[:-3] if field.endswith(".lc") else field
        for h in r["hits"]["hits"]:
            s = h["_source"]
            if src_field == "displayText":
                v = s.get("displayText")
            else:
                v = (s.get("attributes") or {}).get(src_field.split(".")[-1])
            if v and v not in out:
                out.append(v)
            if len(out) >= 5:
                break
        return {"suggestions": out}

    # ------------------------------------------------------------------ full-text / attribute search
    async def fulltext(self, query: str, exclude_deleted: bool, limit: int, offset: int) -> dict:
        p = {"query": query, "excludeDeletedEntities": exclude_deleted, "limit": limit, "offset": offset}
        q, _ = self.build_basic_query(p)
        r = await self.store.search(self.store.entities, q, size=min(limit, self.settings.search_max_limit),
                                    from_=offset, sort=["_score", {"guid": "asc"}])
        docs = [h["_source"] for h in r["hits"]["hits"]]
        headers = await self._headers(docs, [])
        res: Dict[str, Any] = {"queryType": "FULL_TEXT", "queryText": query,
                               "approximateCount": r["hits"]["total"]["value"]}
        if headers:
            res["entities"] = headers
            res["fullTextResult"] = [{"entity": h, "score": hit.get("_score") or 0.0}
                                     for h, hit in zip(headers, r["hits"]["hits"])]
        return res

    async def attribute(self, attr_name: str, prefix: str, type_name: Optional[str], limit: int, offset: int) -> dict:
        if not attr_name or prefix is None:
            raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, "attrName and attrValuePrefix are required")
        type_names = self._type_set(type_name, True) or []
        ref = resolve_field(self.reg, attr_name, type_names)
        filters: List[dict] = [{"prefix": {ref.field + (".lc" if ref.has_lc else ""): {"value": str(prefix).lower() if ref.has_lc else prefix,
                                                                                        "case_insensitive": True}}}]
        if type_names:
            filters.append({"terms": {"typeName": type_names}})
        r = await self.store.search(self.store.entities, {"bool": {"filter": filters}}, size=limit, from_=offset,
                                    sort=[{"displayText.lc": {"order": "asc", "unmapped_type": "keyword"}}, {"guid": "asc"}])
        docs = [h["_source"] for h in r["hits"]["hits"]]
        res: Dict[str, Any] = {"queryType": "ATTRIBUTE", "approximateCount": r["hits"]["total"]["value"]}
        if docs:
            res["entities"] = await self._headers(docs, [attr_name])
        return res

    # ------------------------------------------------------------------ relationship search
    async def related_entities(self, guid: str, relation: str, attributes: List[str], sort_by: Optional[str],
                               sort_order: Optional[str], exclude_deleted: bool, include_classification_attrs: bool,
                               get_count: bool, limit: int, offset: int) -> dict:
        reg = self.reg
        doc = await self.store.get(self.store.entities, guid)
        if doc is None:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, guid)
        et = reg.entities.get(doc["typeName"])
        ends = (et.relationship_attributes.get(relation) if et else None) or []
        if not ends:
            raise AtlasBaseException(AtlasErrorCode.INVALID_RELATIONSHIP_TYPE, doc["typeName"], guid)
        should = []
        for e in ends:
            should.append({"bool": {"filter": [{"term": {"typeName": e.rel.name}}, {"term": {f"end{e.end}Guid": guid}}]}})
        rq: Dict[str, Any] = {"bool": {"should": should, "minimum_should_match": 1}}
        if exclude_deleted:
            rq["bool"]["filter"] = [{"term": {"status": "ACTIVE"}}]
        else:
            rq["bool"]["filter"] = [{"bool": {"should": [{"term": {"status": "ACTIVE"}}, {"term": {"deletedByEntity": True}}],
                                              "minimum_should_match": 1}}]
        other_guids: List[str] = []
        async for _, r in self.store.scan(self.store.relationships, rq, limit=self.settings.max_relationships_per_entity):
            other_guids.append(r["end2Guid"] if r["end1Guid"] == guid else r["end1Guid"])
        other_guids = list(dict.fromkeys(other_guids))
        res: Dict[str, Any] = {"queryType": "BASIC", "approximateCount": -1,
                               "searchParameters": {"guid": guid, "relation": relation, "limit": limit, "offset": offset}}
        if not other_guids:
            res["approximateCount"] = 0
            return res
        filters: List[dict] = [{"terms": {"guid": other_guids}}]
        if exclude_deleted:
            filters.append({"term": {"status": "ACTIVE"}})
        other_types = sorted({e.other_type for e in ends})
        sort = self._sort(sort_by, sort_order, other_types, False)
        r = await self.store.search(self.store.entities, {"bool": {"filter": filters}}, size=limit, from_=offset, sort=sort)
        docs = [h["_source"] for h in r["hits"]["hits"]]
        res["approximateCount"] = r["hits"]["total"]["value"] if (get_count or offset == 0) else -1
        if docs:
            res["entities"] = await self._headers(docs, attributes, include_classification_attrs)
        return res

    async def relations(self, p: Dict[str, Any]) -> dict:
        """Relationship search (Atlas RelationshipSearchParameters)."""
        reg = self.reg
        name = p.get("relationshipName")
        if not name or name not in reg.relationships or reg.relationships[name].synthetic:
            raise AtlasBaseException(AtlasErrorCode.UNKNOWN_TYPENAME, name)
        limit = max(0, min(_int(p.get("limit"), 25), self.settings.search_max_limit))
        offset = max(0, _int(p.get("offset"), 0))
        filters: List[dict] = [{"term": {"typeName": name}}, {"term": {"status": "ACTIVE"}}]
        rf = criteria_query(reg, p.get("relationshipFilters"), [name], scope="relationship")
        if rf:
            filters.append(rf)
        order = "desc" if str(p.get("sortOrder") or "").upper().startswith("DESC") else "asc"
        if p.get("sortBy"):
            try:
                ref = resolve_field(reg, p["sortBy"], [name], scope="relationship")
                sort = [{ref.field + (".lc" if ref.has_lc else ""): {"order": order, "unmapped_type": "keyword"}},
                        {"guid": "asc"}]
            except AtlasBaseException:
                sort = [{"createTime": "desc"}, {"guid": "asc"}]
        else:
            sort = [{"createTime": "desc"}, {"guid": "asc"}]
        r = await self.store.search(self.store.relationships, {"bool": {"filter": filters}}, size=limit, from_=offset,
                                    sort=sort)
        rels = [h["_source"] for h in r["hits"]["hits"]]
        ends = await self.store.mget(self.store.entities, {x for rr in rels for x in (rr["end1Guid"], rr["end2Guid"])})
        out = []
        for rr in rels:
            full = relationship_to_api(reg, rr, ends.get(rr["end1Guid"]), ends.get(rr["end2Guid"]))
            out.append({k: full[k] for k in ("typeName", "attributes", "guid", "status", "propagateTags", "label",
                                              "end1", "end2")})
        res = {"queryType": "RELATIONSHIP", "searchParameters": p, "approximateCount": r["hits"]["total"]["value"]}
        if out:
            res["relations"] = out
        return res


class SavedSearchService:
    KIND = "savedsearch"

    def __init__(self, store: EsStore):
        self.store = store

    async def _find(self, owner: str, name: str) -> Optional[dict]:
        q = {"bool": {"filter": [{"term": {"kind": self.KIND}}, {"term": {"ownerName": owner}}, {"term": {"name": name}}]}}
        r = await self.store.search(self.store.meta, q, size=1)
        hits = r["hits"]["hits"]
        return hits[0]["_source"]["value"] if hits else None

    async def create(self, s: dict, user: str) -> dict:
        s = copy.deepcopy(s)
        if s.get("ownerName") and s["ownerName"] != user:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "invalid data")
        s["ownerName"] = user
        if not s.get("name"):
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "saved search name is required")
        if await self._find(s["ownerName"], s["name"]):
            raise AtlasBaseException(AtlasErrorCode.SAVED_SEARCH_ALREADY_EXISTS, s["name"], s["ownerName"])
        s["guid"] = str(uuid.uuid4())
        s.setdefault("searchType", "BASIC")
        await self._save(s)
        return s

    async def _save(self, s: dict) -> None:
        await self.store.put(self.store.meta, f"{self.KIND}:{s['guid']}",
                             {"kind": self.KIND, "name": s["name"], "ownerName": s["ownerName"], "guid": s["guid"],
                              "updateTime": int(time.time() * 1000), "value": s})

    async def update(self, s: dict, user: str) -> dict:
        cur = await self.get_by_guid(s.get("guid", ""), user)
        if s.get("ownerName") not in (None, user):
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "invalid data")
        merged = {**cur, **{k: v for k, v in s.items() if v is not None}}
        merged["ownerName"] = cur["ownerName"]
        if merged["name"] != cur["name"] and await self._find(cur["ownerName"], merged["name"]):
            raise AtlasBaseException(AtlasErrorCode.SAVED_SEARCH_ALREADY_EXISTS, merged["name"], cur["ownerName"])
        await self._save(merged)
        return merged

    async def get_by_guid(self, guid: str, user: Optional[str] = None) -> dict:
        d = await self.store.get(self.store.meta, f"{self.KIND}:{guid}")
        if d is None:
            raise AtlasBaseException(AtlasErrorCode.SAVED_SEARCH_NOT_FOUND, guid)
        if user is not None and d["value"].get("ownerName") != user:
            # Atlas' checkSavedSearchOwnership
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "invalid data")
        return d["value"]

    async def get_by_name(self, name: str, owner: str) -> dict:
        s = await self._find(owner, name)
        if s is None:
            raise AtlasBaseException(AtlasErrorCode.SAVED_SEARCH_NOT_FOUND, name)
        return s

    async def list(self, owner: str) -> List[dict]:
        q = {"bool": {"filter": [{"term": {"kind": self.KIND}}, {"term": {"ownerName": owner}}]}}
        r = await self.store.search(self.store.meta, q, size=1000, sort=[{"name": "asc"}])
        return [h["_source"]["value"] for h in r["hits"]["hits"]]

    async def delete(self, guid: str, user: str) -> None:
        await self.get_by_guid(guid, user)
        await self.store.delete(self.store.meta, f"{self.KIND}:{guid}")
