"""Elastic App Search compatible search on plain Elasticsearch.

The Aurelius frontend sends App Search queries (``POST /api/as/v1/engines/<engine>/search.json``) through the
reverse proxy.  Enterprise Search is gone, so pyatlas translates the request into an Elasticsearch query on the
engine's index and returns the App Search response format:

request                                              Elasticsearch
``query`` ("" = everything)                          ``multi_match`` over the engine's search fields (``.text``
                                                     sub-fields, weights as boosts), all terms required, plus a
                                                     phrase-prefix match on the name for type-ahead
``filters`` {field: value | [values]},                ``terms`` on the keyword field; arrays are OR, ``all`` /
{field: {from, to}}, {all|any|none: [...]}           ``any`` / ``none`` nest as bool must / should / must_not
``facets`` {field: [{type: value, size}]}            ``terms`` aggregation on the filtered result set
``sort`` {field: dir} | [{field: dir}] | _score      sort on the keyword / number field
``page`` {current, size}                             from / size (size <= 1000, from + size <= 10000)
``result_fields`` {field: {raw, snippet}}            ``_source`` + snippets with ``<em>`` highlighting
"""
from __future__ import annotations

import html
import math
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode
from .engines import ENGINES

MAX_PAGE_SIZE = 1000
MAX_WINDOW = 10000


def _bad(msg: str) -> AtlasBaseException:
    return AtlasBaseException(AtlasErrorCode.BAD_REQUEST, msg)


class AppSearchError(ValueError):
    """Invalid request in App Search terms (reported as {"errors": [...]}, HTTP 400)."""


def _field_kind(engine: str, field: str) -> str:
    if field == "id":
        return "text"
    return ENGINES[engine]["schema"].get(field, "text")


def build_filter(engine: str, f: Any) -> dict:
    if isinstance(f, list):
        return {"bool": {"filter": [build_filter(engine, x) for x in f]}}
    if not isinstance(f, dict):
        raise AppSearchError("Filters must be an object")
    clauses = []
    for key, value in f.items():
        if key in ("all", "any", "none"):
            items = value if isinstance(value, list) else [value]
            sub = [build_filter(engine, x) for x in items]
            if key == "all":
                clauses.append({"bool": {"filter": sub}})
            elif key == "any":
                clauses.append({"bool": {"should": sub, "minimum_should_match": 1}})
            else:
                clauses.append({"bool": {"must_not": sub}})
            continue
        kind = _field_kind(engine, key)
        if isinstance(value, dict) and ({"from", "to"} & set(value)):
            rng = {}
            if value.get("from") is not None:
                rng["gte"] = value["from"]
            if value.get("to") is not None:
                rng["lt"] = value["to"]
            clauses.append({"range": {key: rng}})
            continue
        values = value if isinstance(value, list) else [value]
        if kind == "number":
            try:
                values = [float(v) for v in values]
            except (TypeError, ValueError):
                raise AppSearchError(f"Filter value for {key} must be a number") from None
        else:
            values = [str(v) for v in values]
        clauses.append({"terms": {key: values}})
    if len(clauses) == 1:
        return clauses[0]
    return {"bool": {"filter": clauses}}


def build_query(engine: str, text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {"match_all": {}}
    fields = [f"{name}.text^{weight:g}" if _field_kind(engine, name) != "number" else f"{name}^{weight:g}"
              for name, weight in ENGINES[engine]["search_fields"].items() if _field_kind(engine, name) != "number"]
    should = [{"multi_match": {"query": text, "fields": fields, "type": "best_fields", "operator": "and"}}]
    if "name" in ENGINES[engine]["schema"]:
        should.append({"multi_match": {"query": text, "fields": ["name.text^2"], "type": "phrase_prefix"}})
    return {"bool": {"should": should, "minimum_should_match": 1}}


def build_sort(engine: str, sort: Any) -> Optional[list]:
    if not sort:
        return None
    items = sort if isinstance(sort, list) else [{k: v} for k, v in sort.items()] if isinstance(sort, dict) else None
    if items is None:
        raise AppSearchError("Sort must be an object or an array of objects")
    out = []
    for it in items:
        if not isinstance(it, dict) or len(it) != 1:
            raise AppSearchError("Each sort entry must have exactly one field")
        (field, direction), = it.items()
        direction = str(direction).lower()
        if direction not in ("asc", "desc"):
            raise AppSearchError(f"Sort direction for {field} must be asc or desc")
        if field != "_score" and field != "id" and field not in ENGINES[engine]["schema"]:
            raise AppSearchError(f"{field} is not a valid sort field")
        out.append({field: {"order": direction}} if field != "_score" else {"_score": {"order": direction}})
    return out


def build_aggs(engine: str, facets: Any) -> Tuple[dict, dict]:
    """(aggs, facet spec by field) - only ``value`` facets (the only kind the frontend uses)."""
    aggs, spec = {}, {}
    for field, defs in (facets or {}).items():
        items = defs if isinstance(defs, list) else [defs]
        for i, d in enumerate(items):
            if not isinstance(d, dict) or d.get("type", "value") != "value":
                raise AppSearchError(f"Facet type for {field} is not supported (only value facets)")
            size = int(d.get("size", 10))
            if not 1 <= size <= 250:
                raise AppSearchError("Facet size must be between 1 and 250")
            name = f"f{len(aggs)}"
            order = {"_count": "desc"}
            if isinstance(d.get("sort"), dict) and "value" in d["sort"]:
                order = {"_key": d["sort"]["value"]}
            aggs[name] = {"terms": {"field": field, "size": size, "order": order}}
            spec.setdefault(field, []).append((name, d.get("name")))
    return aggs, spec


def snippet(text: Any, query: str, size: int) -> Optional[str]:
    if text is None:
        return None
    if isinstance(text, list):
        text = ", ".join(str(t) for t in text)
    s = str(text)
    terms = [t for t in re.split(r"\W+", (query or "").lower()) if len(t) > 1]
    low = s.lower()
    start = 0
    if terms:
        hits = [low.find(t) for t in terms if low.find(t) >= 0]
        if hits:
            start = max(0, min(hits) - size // 4)
    fragment = s[start:start + size]
    out = html.escape(fragment)
    for t in sorted(set(terms), key=len, reverse=True):
        out = re.sub(f"(?i)({re.escape(html.escape(t))})", r"<em>\1</em>", out)
    return out


def format_result(engine: str, hit: dict, query: str, result_fields: Optional[dict]) -> dict:
    src = hit.get("_source") or {}
    fields = result_fields if result_fields else {k: {"raw": {}} for k in src}
    out: Dict[str, Any] = {}
    for name, how in fields.items():
        how = how or {"raw": {}}
        entry: Dict[str, Any] = {}
        value = src.get(name)
        if "raw" in how:
            entry["raw"] = value
        if "snippet" in how:
            opts = how.get("snippet") or {}
            sn = snippet(value, query, int(opts.get("size", 100)))
            if sn is None or (query and "<em>" not in sn and not opts.get("fallback", True)):
                sn = None
            entry["snippet"] = sn
        out[name] = entry
    out["id"] = {"raw": src.get("id", hit.get("_id"))}
    out["_meta"] = {"id": hit.get("_id"), "engine": engine, "score": hit.get("_score") or 0.0}
    return out


async def search(store, index: str, engine: str, request: dict) -> dict:
    if engine not in ENGINES:
        raise AppSearchError(f"Could not find engine {engine}")
    if not isinstance(request, dict):
        raise AppSearchError("Request body must be an object")
    text = request.get("query", "")
    if not isinstance(text, str):
        raise AppSearchError("Query must be a string")
    page = request.get("page") or {}
    current = int(page.get("current", 1) or 1)
    size = int(page.get("size", 10) or 10)
    if current < 1 or not 1 <= size <= MAX_PAGE_SIZE:
        raise AppSearchError(f"Page size must be between 1 and {MAX_PAGE_SIZE}, current page at least 1")
    if (current - 1) * size + size > MAX_WINDOW:
        raise AppSearchError(f"Only the first {MAX_WINDOW} results can be paged through")
    query = build_query(engine, text)
    if request.get("filters"):
        query = {"bool": {"must": [query], "filter": [build_filter(engine, request["filters"])]}}
    aggs, facet_spec = build_aggs(engine, request.get("facets"))
    sort = build_sort(engine, request.get("sort"))
    r = await store.search(index, query, size=size, from_=(current - 1) * size, sort=sort, aggs=aggs or None)
    total = r["hits"]["total"]["value"] if isinstance(r["hits"]["total"], dict) else r["hits"]["total"]
    results = [format_result(engine, h, text, request.get("result_fields")) for h in r["hits"]["hits"]]
    facets = {}
    for field, specs in facet_spec.items():
        facets[field] = []
        for agg_name, facet_name in specs:
            buckets = (r.get("aggregations") or {}).get(agg_name, {}).get("buckets", [])
            item = {"type": "value", "data": [{"value": _facet_value(engine, field, b["key"]), "count": b["doc_count"]}
                                              for b in buckets]}
            if facet_name:
                item["name"] = facet_name
            facets[field].append(item)
    meta = {"alerts": [], "warnings": [], "precision": 2,
            "page": {"current": current, "total_pages": max(1, math.ceil(total / size)) if total else 0,
                     "total_results": total, "size": size},
            "engine": {"name": engine, "type": "default"}, "request_id": str(uuid.uuid4())}
    out = {"meta": meta, "results": results}
    if facet_spec:
        out["facets"] = facets
    return out


def _facet_value(engine: str, field: str, key: Any) -> Any:
    if _field_kind(engine, field) == "number":
        try:
            f = float(key)
            return int(f) if f.is_integer() else f
        except (TypeError, ValueError):
            return key
    return key


async def get_documents(store, index: str, ids: List[str]) -> List[Optional[dict]]:
    """``GET /api/as/v1/engines/<engine>/documents?ids[]=...``: the documents in request order, null if missing."""
    docs = await store.mget(index, ids)
    return [docs.get(i) for i in ids]
