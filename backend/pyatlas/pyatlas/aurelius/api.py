"""/api/aurelius - endpoints the Aurelius frontend (apps/atlas) calls besides the Atlas v2 API."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from ..authz import Privilege
from ..web.common import json_body, svc, user_of
from . import appsearch
from .engines import ENGINES

router = APIRouter(prefix="/api/aurelius")

# one JSON line per event; ship these logs to Elasticsearch/Kibana like the other pyatlas logs
clickstream_log = logging.getLogger("pyatlas.aurelius.clickstream")
frontend_errors = logging.getLogger("pyatlas.aurelius.frontend")

_MAX_FIELD = 2000


def _clip(v: Any) -> Any:
    if isinstance(v, str):
        return v[:_MAX_FIELD]
    if isinstance(v, (int, float, bool)) or v is None:
        return v
    return json.dumps(v, default=str)[:_MAX_FIELD]


@router.post("/repository/log")
async def log_clickstream(request: Request):
    """Frontend clickstream event (``libs/repository`` ``logClickstreamEvent``: app, timestamp, url, userid).
    Logged with the authenticated user; the ``userid`` sent by the browser is not trusted."""
    body = await json_body(request, default={}) or {}
    event = {"type": "clickstream", "user": user_of(request), "app": _clip(body.get("app")),
             "url": _clip(body.get("url")), "timestamp": body.get("timestamp") or int(time.time() * 1000)}
    clickstream_log.info(json.dumps(event))
    return Response(status_code=204)


@router.post("/repository/error")
async def report_error(request: Request):
    """Error report of the frontend (``reportError``: app, version, error, state)."""
    body = await json_body(request, default={}) or {}
    error = body.get("error") if isinstance(body.get("error"), dict) else {"message": body.get("error")}
    event = {"type": "frontend-error", "user": user_of(request), "app": _clip(body.get("app")),
             "version": _clip(body.get("version")), "message": _clip((error or {}).get("message")),
             "stack": _clip((error or {}).get("stack"))}
    frontend_errors.warning(json.dumps(event))
    return Response(status_code=204)


# ------------------------------------------------------------------ App Search compatible search
def _aurelius(request: Request):
    a = svc(request).aurelius
    if a is None:
        return None
    return a


def _engine_error(engine: str) -> JSONResponse:
    return JSONResponse({"errors": [f"Could not find engine {engine}"]}, status_code=404)


@router.post("/search/{engine}")
@router.post("/search/{engine}/search")
@router.post("/search/{engine}/search.json")
@router.post("/as/v1/engines/{engine}/search")
@router.post("/as/v1/engines/{engine}/search.json")
async def app_search(engine: str, request: Request):
    """App Search ``search`` API on the Aurelius engines (atlas-dev, atlas-dev-quality, atlas-dev-gov-quality)."""
    a = _aurelius(request)
    if a is None or engine not in ENGINES:
        return _engine_error(engine)
    body = await json_body(request, default={}) or {}
    try:
        return await appsearch.search(a.store, a.index(engine), engine, body)
    except appsearch.AppSearchError as e:
        return JSONResponse({"errors": [str(e)]}, status_code=400)


@router.get("/search/{engine}/documents")
@router.get("/as/v1/engines/{engine}/documents")
@router.post("/search/{engine}/documents/get")
async def app_search_documents(engine: str, request: Request):
    """``GET documents?ids[]=..`` (the frontend's getAppSearchEntity)."""
    a = _aurelius(request)
    if a is None or engine not in ENGINES:
        return _engine_error(engine)
    ids = request.query_params.getlist("ids[]") or request.query_params.getlist("ids")
    if request.method == "POST":
        ids = list(await json_body(request, default=[]) or [])
    return await appsearch.get_documents(a.store, a.index(engine), [str(i) for i in ids][:100])


@router.post("/admin/search/rebuild")
async def rebuild_search_documents(request: Request):
    """Recompute all search documents from the metadata (admin)."""
    a = _aurelius(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    svc(request).authz.verify_admin(Privilege.ADMIN_IMPORT, "rebuild the Aurelius search documents")
    await a.flush()
    return await a.rebuild()


@router.get("/admin/search/status")
async def search_status(request: Request):
    a = _aurelius(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    counts = {e: await a.store.count(a.index(e), {"match_all": {}}) for e in ENGINES}
    return {"documents": counts, "lastRebuild": a.last_rebuild}


# ------------------------------------------------------------------ lineage model (model viewer)
@router.get("/lineage_model")
@router.get("/lineage_model/")
async def lineage_model(request: Request, guid: str, depth: int = 3, direction: str = "BOTH"):
    """The lineage of ``guid`` as an ArchiMate model (formerly m4i-lineage-model + m4i-data2model)."""
    from ..errors import AtlasBaseException
    from .lineage_model import build
    direction = direction.upper()
    if direction not in ("INPUT", "OUTPUT", "BOTH"):
        return JSONResponse({"errorMessage": "direction must be INPUT, OUTPUT or BOTH"}, status_code=400)
    s = svc(request)
    try:
        lineage = await s.lineage.lineage(guid, direction, max(1, min(depth, 10)))
    except AtlasBaseException as e:
        if e.http_status == 404:
            return Response(status_code=204)
        raise
    status, body = build(lineage, guid, s.typedefs.registry)
    if status == 204:
        return Response(status_code=204)
    return body
