"""/api/atlas/v2/types (Atlas ``TypesREST``)."""
from __future__ import annotations

import json
import time
from typing import Any, Dict

from fastapi import APIRouter, Request, Response

from ..typesystem.registry import (BUSINESS_METADATA, CATEGORY_LIST_KEYS as CATEGORY_KEYS, CLASSIFICATION, ENTITY, ENUM,
                                   RELATIONSHIP, STRUCT)
from .common import json_body, svc, user_of

router = APIRouter(prefix="/api/atlas/v2/types")


def _filter_params(request: Request) -> Dict[str, Any]:
    p: Dict[str, Any] = {}
    for k, v in request.query_params.multi_items():
        if k in ("supertype", "notsupertype"):
            p.setdefault(k, []).append(v)
        else:
            p[k] = v
    return p


@router.get("/typedef/name/{name}")
async def typedef_by_name(name: str, request: Request):
    return svc(request).typedefs.get_by_name(name)


@router.get("/typedef/guid/{guid}")
async def typedef_by_guid(guid: str, request: Request):
    return svc(request).typedefs.get_by_guid(guid)


@router.get("/typedefs/headers")
async def typedef_headers(request: Request):
    return svc(request).typedefs.headers(_filter_params(request))


@router.get("/typedefs")
async def typedefs(request: Request):
    return svc(request).typedefs.search(_filter_params(request))


def _category_routes(path: str, category: str):
    async def by_name(name: str, request: Request):
        return svc(request).typedefs.get_by_name(name, category)

    async def by_guid(guid: str, request: Request):
        return svc(request).typedefs.get_by_guid(guid, category)
    router.add_api_route(f"/{path}/name/{{name}}", by_name, methods=["GET"], name=f"{path}_by_name")
    router.add_api_route(f"/{path}/guid/{{guid}}", by_guid, methods=["GET"], name=f"{path}_by_guid")


for _path, _cat in (("enumdef", ENUM), ("structdef", STRUCT), ("classificationdef", CLASSIFICATION),
                    ("entitydef", ENTITY), ("relationshipdef", RELATIONSHIP), ("businessmetadatadef", BUSINESS_METADATA)):
    _category_routes(_path, _cat)


async def _audit(request: Request, op: str, types_def: dict, start: int) -> None:
    names = [d.get("name") for lst in types_def.values() if isinstance(lst, list) for d in lst if isinstance(d, dict)]
    await svc(request).audits.add(op, user_of(request), ",".join(n for n in names if n), json.dumps(types_def),
                                  len(names), start, int(time.time() * 1000),
                                  request.client.host if request.client else "")


@router.post("/typedefs")
async def create_typedefs(request: Request):
    start = int(time.time() * 1000)
    body = await json_body(request)
    res = await svc(request).typedefs.create(body, user_of(request))
    await _audit(request, "TYPE_DEF_CREATE", res, start)
    return res


@router.put("/typedefs")
async def update_typedefs(request: Request):
    start = int(time.time() * 1000)
    body = await json_body(request)
    res = await svc(request).typedefs.update(body, user_of(request))
    await _audit(request, "TYPE_DEF_UPDATE", res, start)
    return res


@router.delete("/typedefs", status_code=204)
async def delete_typedefs(request: Request):
    start = int(time.time() * 1000)
    body = await json_body(request)
    s = svc(request)
    await s.typedefs.delete(body, s.type_has_instances)
    await _audit(request, "TYPE_DEF_DELETE", body, start)
    return Response(status_code=204)


@router.delete("/typedef/name/{name}", status_code=204)
async def delete_typedef(name: str, request: Request):
    start = int(time.time() * 1000)
    s = svc(request)
    d = s.typedefs.get_by_name(name)
    await s.typedefs.delete_by_names([name], s.type_has_instances)
    await _audit(request, "TYPE_DEF_DELETE", {CATEGORY_KEYS[d["category"]]: [d]}, start)
    return Response(status_code=204)
