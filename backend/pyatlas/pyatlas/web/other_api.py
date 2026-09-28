"""Relationship, discovery and lineage endpoints."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import FileResponse

from ..errors import AtlasBaseException, AtlasErrorCode
from ..safety import neutralize_formula
from .common import json_body, qbool, svc, unique_attrs_from_query, user_of

relationship_router = APIRouter(prefix="/api/atlas/v2/relationship")
search_router = APIRouter(prefix="/api/atlas/v2/search")
lineage_router = APIRouter(prefix="/api/atlas/v2/lineage")


# ======================================================================== relationships
@relationship_router.post("")
async def create_relationship(request: Request):
    return await svc(request).entities.create_relationship(await json_body(request), user_of(request))


@relationship_router.put("")
async def update_relationship(request: Request):
    return await svc(request).entities.update_relationship(await json_body(request), user_of(request))


@relationship_router.get("/guid/{guid}")
async def get_relationship(guid: str, request: Request, extendedInfo: bool = False):
    return await svc(request).entities.get_relationship(guid, extendedInfo)


@relationship_router.delete("/guid/{guid}", status_code=204)
async def delete_relationship(guid: str, request: Request):
    await svc(request).entities.delete_relationship(guid, user_of(request))
    return Response(status_code=204)


# ======================================================================== search
def _scrub(request: Request, result: dict) -> dict:
    """Atlas scrubs search results: entities the user may not read keep only their type (guid "-1")."""
    return svc(request).authz.scrub_search_result(result) if isinstance(result, dict) else result


def _scrub_quick(request: Request, result: dict) -> dict:
    if isinstance(result, dict) and isinstance(result.get("searchResults"), dict):
        _scrub(request, result["searchResults"])
    return result


@search_router.get("/basic")
async def basic_get(request: Request, query: Optional[str] = None, typeName: Optional[str] = None,
                    classification: Optional[str] = None, sortBy: Optional[str] = None, sortOrder: Optional[str] = None,
                    excludeDeletedEntities: bool = False, limit: int = 100, offset: int = 0, marker: Optional[str] = None):
    p = {"query": query, "typeName": typeName, "classification": classification, "sortBy": sortBy,
         "sortOrder": sortOrder, "excludeDeletedEntities": excludeDeletedEntities, "limit": limit, "offset": offset}
    return _scrub(request, await svc(request).search.basic({k: v for k, v in p.items() if v is not None}))


@search_router.post("/basic")
async def basic_post(request: Request):
    return _scrub(request, await svc(request).search.basic(await json_body(request)))


@search_router.get("/quick")
async def quick_get(request: Request, query: Optional[str] = None, typeName: Optional[str] = None,
                    excludeDeletedEntities: bool = True, offset: int = 0, limit: int = 25,
                    sortBy: Optional[str] = None, sortOrder: Optional[str] = None):
    return _scrub_quick(request, await svc(request).search.quick({
        "query": query, "typeName": typeName, "excludeDeletedEntities": excludeDeletedEntities, "offset": offset,
        "limit": limit, "sortBy": sortBy, "sortOrder": sortOrder}))


@search_router.post("/quick")
async def quick_post(request: Request):
    return _scrub_quick(request, await svc(request).search.quick(await json_body(request)))


@search_router.get("/suggestions")
async def suggestions(request: Request, prefixString: str = "", fieldName: Optional[str] = None):
    return await svc(request).search.suggestions(prefixString, fieldName)


@search_router.get("/fulltext")
async def fulltext(request: Request, query: str, excludeDeletedEntities: bool = False, limit: int = 100, offset: int = 0):
    return _scrub(request, await svc(request).search.fulltext(query, excludeDeletedEntities, limit, offset))


@search_router.get("/attribute")
async def attribute_search(request: Request, attrName: str, attrValuePrefix: str, typeName: Optional[str] = None,
                           limit: int = 100, offset: int = 0):
    return _scrub(request, await svc(request).search.attribute(attrName, attrValuePrefix, typeName, limit, offset))


@search_router.get("/dsl")
async def dsl(request: Request, query: str = "", typeName: Optional[str] = None, classification: Optional[str] = None,
              limit: int = 100, offset: int = 0):
    return _scrub(request, await svc(request).dsl_search(query, typeName, classification, limit, offset))


@search_router.get("/relationship")
async def related(request: Request, guid: str, relation: str, attributes: List[str] = Query(default=[]),
                  sortBy: Optional[str] = None, sortOrder: Optional[str] = None, excludeDeletedEntities: bool = False,
                  includeClassificationAttributes: bool = False, getApproximateCount: bool = False,
                  limit: int = 100, offset: int = 0):
    return _scrub(request, await svc(request).search.related_entities(
        guid, relation, attributes, sortBy, sortOrder, excludeDeletedEntities, includeClassificationAttributes,
        getApproximateCount, limit, offset))


@search_router.post("/relations")
async def relations_post(request: Request):
    return await svc(request).search.relations(await json_body(request))


@search_router.get("/relations")
async def relations_get(request: Request, relationshipName: str, limit: int = 25, offset: int = 0,
                        sortBy: Optional[str] = None, sortOrder: Optional[str] = None):
    return await svc(request).search.relations({"relationshipName": relationshipName, "limit": limit, "offset": offset,
                                                "sortBy": sortBy, "sortOrder": sortOrder})


# ---- saved searches
@search_router.post("/saved")
async def saved_create(request: Request):
    return await svc(request).saved.create(await json_body(request), user_of(request))


@search_router.put("/saved")
async def saved_update(request: Request):
    return await svc(request).saved.update(await json_body(request), user_of(request))


def _own_user(request: Request, user: Optional[str]) -> str:
    """Atlas: a user may only address his own saved searches (``user`` parameter = current user)."""
    me = user_of(request)
    if user and user != me:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "invalid data")
    return me


@search_router.get("/saved")
async def saved_list(request: Request, user: Optional[str] = None):
    return await svc(request).saved.list(_own_user(request, user))


@search_router.get("/saved/execute/guid/{guid}")
async def saved_exec_guid(guid: str, request: Request):
    s = await svc(request).saved.get_by_guid(guid, user_of(request))
    return await _execute_saved(request, s)


@search_router.get("/saved/execute/{name}")
async def saved_exec_name(name: str, request: Request, user: Optional[str] = None):
    s = await svc(request).saved.get_by_name(name, _own_user(request, user))
    return await _execute_saved(request, s)


@search_router.get("/saved/{name}")
async def saved_get(name: str, request: Request, user: Optional[str] = None):
    return await svc(request).saved.get_by_name(name, _own_user(request, user))


@search_router.delete("/saved/{guid}", status_code=204)
async def saved_delete(guid: str, request: Request):
    await svc(request).saved.delete(guid, user_of(request))
    return Response(status_code=204)


async def _execute_saved(request: Request, s: dict):
    p = s.get("searchParameters") or {}
    if s.get("searchType") == "ADVANCED":
        return _scrub(request, await svc(request).dsl_search(p.get("query") or "", p.get("typeName"), p.get("classification"),
                                                             p.get("limit", 100), p.get("offset", 0)))
    return _scrub(request, await svc(request).search.basic(p))


SEARCH_DL = "search_result_downloads"


def _csv_cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, dict) and "guid" in v:
        return str((v.get("uniqueAttributes") or {}).get("qualifiedName") or v.get("displayText") or v["guid"])
    if isinstance(v, list):
        return ",".join(_csv_cell(x) for x in v)
    return str(v)


def _write_search_csv(path, result: dict, label_map: dict, query_type: str) -> None:
    import csv as _csv
    entities = result.get("entities") or []
    attrs = result.get("attributes")
    if not entities and not attrs:
        return
    label_map = dict(label_map or {})
    label_map["Owner"] = "owner"
    label_map["Description"] = "description"
    defaults = ["Type name", "Name", "Classifications", "Terms"]
    if query_type == "DSL" and not entities and attrs:
        headers = list(attrs.get("name") or [])
        rows = [[_csv_cell(v) for v in row] for row in attrs.get("values") or []]
    else:
        headers = defaults + list(label_map.keys())
        rows = []
        for e in entities:
            row = [e.get("typeName"), e.get("displayText") or e.get("guid"),
                   ",".join(e.get("classificationNames") or []), ",".join(e.get("meaningNames") or [])]
            for label in list(label_map.keys()):
                row.append(_csv_cell((e.get("attributes") or {}).get(label_map[label])))
            rows.append(row)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = _csv.writer(f, quoting=_csv.QUOTE_ALL)
        w.writerow(headers)
        w.writerows([[neutralize_formula(c) for c in r] for r in rows])   # CSV formula injection


def _stamp() -> str:
    import datetime as _dt
    return _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]


@search_router.post("/basic/download/create_file", status_code=204)
async def basic_download(request: Request):
    body = await json_body(request)
    s = svc(request)
    params = dict(body.get("searchParameters") or {})
    if not any(params.get(k) for k in ("typeName", "classification", "termName", "query")):
        raise AtlasBaseException(AtlasErrorCode.INVALID_SEARCH_PARAMS)
    label_map = body.get("attributeLabelMap") or {}
    params["limit"] = s.settings.search_max_limit
    params["offset"] = 0
    params["attributes"] = sorted(set(params.get("attributes") or []) | set(label_map.values()) | {"owner", "description"})
    user = user_of(request)

    async def writer(path):
        _write_search_csv(path, s.authz.scrub_search_result(await s.search.basic(params)), label_map, "BASIC")
    s.downloads.submit(SEARCH_DL, user, f"{user}_BASIC_{_stamp()}.csv", writer)
    return Response(status_code=204)


@search_router.post("/dsl/download/create_file", status_code=204)
async def dsl_download(request: Request):
    body = await json_body(request)
    s = svc(request)
    p = body.get("searchParameters") or {}
    if not (p.get("query") or p.get("typeName") or p.get("classification")):
        raise AtlasBaseException(AtlasErrorCode.INVALID_SEARCH_PARAMS)
    user = user_of(request)

    async def writer(path):
        res = await s.dsl_search(p.get("query") or "", p.get("typeName"), p.get("classification"),
                                 s.settings.search_max_limit, int(p.get("offset") or 0))
        _write_search_csv(path, s.authz.scrub_search_result(res), {}, "DSL")
    s.downloads.submit(SEARCH_DL, user, f"{user}_DSL_{_stamp()}.csv", writer)
    return Response(status_code=204)


@search_router.get("/download/status")
async def download_status(request: Request):
    return svc(request).downloads.status(SEARCH_DL, user_of(request))


@search_router.get("/download/{filename}")
async def download_file(filename: str, request: Request):
    path = svc(request).downloads.resolve(SEARCH_DL, user_of(request), filename)
    if not path.is_file():
        return Response(status_code=204)
    return FileResponse(path, media_type="application/octet-stream", filename=path.name)


# ======================================================================== lineage
@lineage_router.get("/uniqueAttribute/type/{type_name}")
async def lineage_by_unique(type_name: str, request: Request, direction: str = "BOTH", depth: int = 3,
                            hideProcess: bool = False):
    s = svc(request)
    guid = await s.entities.get_guid_by_unique_attributes(type_name, unique_attrs_from_query(request))
    return await s.lineage.lineage(guid, direction, depth, hideProcess)


@lineage_router.get("/{guid}")
async def lineage_get(guid: str, request: Request, direction: str = "BOTH", depth: int = 3, hideProcess: bool = False):
    return await svc(request).lineage.lineage(guid, direction, depth, hideProcess)


@lineage_router.post("/{guid}")
async def lineage_on_demand(guid: str, request: Request):
    body = await json_body(request, default={})
    s = svc(request)
    return await s.lineage.lineage_on_demand(guid, body or {}, s.settings.lineage_on_demand_default_node_count)
