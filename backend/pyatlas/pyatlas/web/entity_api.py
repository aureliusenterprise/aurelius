"""/api/atlas/v2/entity (Atlas ``EntityREST``)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query, Request, Response, UploadFile

from ..errors import AtlasBaseException, AtlasErrorCode
from .common import bulk_unique_attrs_from_query, json_body, qbool, svc, unique_attrs_from_query, user_of

router = APIRouter(prefix="/api/atlas/v2/entity")


async def _guid_for_unique(request: Request, type_name: str) -> str:
    attrs = unique_attrs_from_query(request)
    if not attrs:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "unique attributes (attr:<name>=<value>) are required")
    return await svc(request).entities.get_guid_by_unique_attributes(type_name, attrs)


# ------------------------------------------------------------------ read
@router.get("/guid/{guid}")
async def get_by_id(guid: str, request: Request, minExtInfo: bool = False, ignoreRelationships: bool = False):
    return await svc(request).entities.get_by_guid(guid, minExtInfo, ignoreRelationships)


@router.get("/guid/{guid}/header")
async def get_header(guid: str, request: Request):
    return await svc(request).entities.get_header(guid)


@router.get("/uniqueAttribute/type/{type_name}/header")
async def get_header_by_unique(type_name: str, request: Request):
    guid = await _guid_for_unique(request, type_name)
    return await svc(request).entities.get_header(guid)


@router.get("/uniqueAttribute/type/{type_name}")
async def get_by_unique(type_name: str, request: Request, minExtInfo: bool = False, ignoreRelationships: bool = False):
    guid = await _guid_for_unique(request, type_name)
    return await svc(request).entities.get_by_guid(guid, minExtInfo, ignoreRelationships)


@router.get("/bulk/uniqueAttribute/type/{type_name}")
async def get_bulk_by_unique(type_name: str, request: Request, minExtInfo: bool = False, ignoreRelationships: bool = False):
    s = svc(request)
    guids = []
    for attrs in bulk_unique_attrs_from_query(request):
        g = await s.entities.find_guid_by_unique_attributes(type_name, attrs)
        if g:
            guids.append(g)
    if not guids:
        return {"entities": [], "referredEntities": {}}
    return await s.entities.get_by_guids(guids, minExtInfo, ignoreRelationships)


@router.get("/bulk")
async def get_by_guids(request: Request, guid: List[str] = Query(default=[]), minExtInfo: bool = False,
                       ignoreRelationships: bool = False):
    if not guid:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "guid parameter is required")
    return await svc(request).entities.get_by_guids(guid, minExtInfo, ignoreRelationships)


@router.get("/bulk/headers")
async def get_headers(request: Request, tagUpdateStartTime: int = 0):
    return {"guidHeaderMap": await svc(request).entities.headers_updated_since(tagUpdateStartTime)}


@router.get("/{guid}/audit")
async def audit(guid: str, request: Request, startKey: Optional[str] = None, count: int = 100,
                auditAction: Optional[str] = None, sortBy: str = "timestamp", sortOrder: str = "desc", offset: int = 0):
    return await svc(request).entities.audit_events(guid, start_key=startKey, count=count, action=auditAction,
                                                    sort_by=sortBy, sort_order=sortOrder, offset=offset)


# ------------------------------------------------------------------ create / update / delete
async def _create_or_update(request: Request, body: dict):
    q = request.query_params
    return await svc(request).entities.create_or_update(
        body, user_of(request),
        replace_classifications=qbool(q.get("replaceClassifications")),
        replace_business_attributes=qbool(q.get("replaceBusinessAttributes")),
        overwrite_business_attributes=qbool(q.get("overwriteBusinessAttributes")),
        append_relationships=True if qbool(q.get("appendRelationshipAttributes")) else None)


@router.post("")
async def create_or_update(request: Request):
    body = await json_body(request)
    if "entity" not in body:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "entity is required")
    return await _create_or_update(request, body)


@router.post("/bulk")
async def create_or_update_bulk(request: Request):
    body = await json_body(request)
    return await _create_or_update(request, body)


@router.put("/guid/{guid}")
async def partial_update_attr(guid: str, request: Request, name: str):
    value = await json_body(request)
    return await svc(request).entities.update_attribute_by_guid(guid, name, value, user_of(request))


@router.put("/uniqueAttribute/type/{type_name}")
async def partial_update_by_unique(type_name: str, request: Request):
    body = await json_body(request)
    attrs = unique_attrs_from_query(request)
    return await svc(request).entities.update_by_unique_attributes(type_name, attrs, body, user_of(request))


@router.delete("/guid/{guid}")
async def delete_by_guid(guid: str, request: Request):
    return await svc(request).entities.delete_by_guids([guid], user_of(request))


@router.delete("/uniqueAttribute/type/{type_name}")
async def delete_by_unique(type_name: str, request: Request):
    guid = await _guid_for_unique(request, type_name)
    return await svc(request).entities.delete_by_guids([guid], user_of(request))


@router.delete("/bulk")
async def delete_by_guids(request: Request, guid: List[str] = Query(default=[])):
    if not guid:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "guid parameter is required")
    return await svc(request).entities.delete_by_guids(guid, user_of(request))


# ------------------------------------------------------------------ classifications
@router.get("/guid/{guid}/classifications")
async def get_classifications(guid: str, request: Request):
    lst = await svc(request).entities.get_classifications(guid)
    return {"list": lst, "startIndex": 0, "pageSize": len(lst), "totalCount": len(lst), "sortType": "NONE"}


@router.get("/guid/{guid}/classification/{name}")
async def get_classification(guid: str, name: str, request: Request):
    for c in await svc(request).entities.get_classifications(guid):
        if c["typeName"] == name:
            return c
    raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_NOT_FOUND, name)


@router.post("/guid/{guid}/classifications", status_code=204)
async def add_classifications(guid: str, request: Request):
    await svc(request).entities.add_classifications(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.put("/guid/{guid}/classifications", status_code=204)
async def update_classifications(guid: str, request: Request):
    await svc(request).entities.update_classifications(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.delete("/guid/{guid}/classification/{name}", status_code=204)
async def delete_classification(guid: str, name: str, request: Request, associatedEntityGuid: Optional[str] = None):
    await svc(request).entities.delete_classification(guid, name, user_of(request), associatedEntityGuid)
    return Response(status_code=204)


@router.post("/uniqueAttribute/type/{type_name}/classifications", status_code=204)
async def add_classifications_by_unique(type_name: str, request: Request):
    guid = await _guid_for_unique(request, type_name)
    await svc(request).entities.add_classifications(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.put("/uniqueAttribute/type/{type_name}/classifications", status_code=204)
async def update_classifications_by_unique(type_name: str, request: Request):
    guid = await _guid_for_unique(request, type_name)
    await svc(request).entities.update_classifications(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.delete("/uniqueAttribute/type/{type_name}/classification/{name}", status_code=204)
async def delete_classification_by_unique(type_name: str, name: str, request: Request):
    guid = await _guid_for_unique(request, type_name)
    await svc(request).entities.delete_classification(guid, name, user_of(request))
    return Response(status_code=204)


@router.post("/bulk/classification", status_code=204)
async def add_classification_bulk(request: Request):
    body = await json_body(request)
    c = body.get("classification")
    guids = body.get("entityGuids") or []
    if not c or not guids:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "classification and entityGuids are required")
    for g in guids:
        await svc(request).entities.add_classifications(g, [c], user_of(request))
    return Response(status_code=204)


@router.post("/bulk/setClassifications")
async def set_classifications(request: Request):
    body = await json_body(request)
    await svc(request).entities.set_classifications(body.get("guidHeaderMap") or {}, user_of(request))
    return []


# ------------------------------------------------------------------ labels
async def _labels(request: Request, guid: str, mode: str):
    labels = await json_body(request, default=[])
    await svc(request).entities.modify_labels(guid, labels or [], mode, user_of(request))
    return Response(status_code=204)


@router.post("/guid/{guid}/labels", status_code=204)
async def set_labels(guid: str, request: Request):
    return await _labels(request, guid, "set")


@router.put("/guid/{guid}/labels", status_code=204)
async def add_labels(guid: str, request: Request):
    return await _labels(request, guid, "add")


@router.delete("/guid/{guid}/labels", status_code=204)
async def remove_labels(guid: str, request: Request):
    return await _labels(request, guid, "remove")


@router.post("/uniqueAttribute/type/{type_name}/labels", status_code=204)
async def set_labels_unique(type_name: str, request: Request):
    return await _labels(request, await _guid_for_unique(request, type_name), "set")


@router.put("/uniqueAttribute/type/{type_name}/labels", status_code=204)
async def add_labels_unique(type_name: str, request: Request):
    return await _labels(request, await _guid_for_unique(request, type_name), "add")


@router.delete("/uniqueAttribute/type/{type_name}/labels", status_code=204)
async def remove_labels_unique(type_name: str, request: Request):
    return await _labels(request, await _guid_for_unique(request, type_name), "remove")


# ------------------------------------------------------------------ business metadata
@router.post("/guid/{guid}/businessmetadata", status_code=204)
async def add_bm(guid: str, request: Request, isOverwrite: bool = False):
    await svc(request).entities.add_or_update_business_attributes(guid, await json_body(request), isOverwrite,
                                                                 user_of(request))
    return Response(status_code=204)


@router.delete("/guid/{guid}/businessmetadata", status_code=204)
async def remove_bm(guid: str, request: Request):
    await svc(request).entities.remove_business_attributes(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.post("/guid/{guid}/businessmetadata/{bm_name}", status_code=204)
async def add_bm_named(guid: str, bm_name: str, request: Request):
    await svc(request).entities.add_or_update_business_attributes(guid, {bm_name: await json_body(request)}, False,
                                                                 user_of(request))
    return Response(status_code=204)


@router.delete("/guid/{guid}/businessmetadata/{bm_name}", status_code=204)
async def remove_bm_named(guid: str, bm_name: str, request: Request):
    await svc(request).entities.remove_business_attributes(guid, {bm_name: await json_body(request, default={})},
                                                          user_of(request))
    return Response(status_code=204)


@router.get("/businessmetadata/import/template")
async def bm_template(request: Request):
    return Response(content="EntityType,EntityUniqueAttributeValue,BusinessAttributeName,BusinessAttributeValue,"
                            "EntityUniqueAttributeName[optional]\n", media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=template_business_metadata"})


@router.post("/businessmetadata/import")
async def bm_import(request: Request, file: UploadFile):
    from ..glossary.service import read_tabular_file
    rows = read_tabular_file(file.filename or "", await file.read())
    return await svc(request).entities.import_business_metadata(rows, user_of(request))
