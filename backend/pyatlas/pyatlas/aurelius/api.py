"""/api/aurelius - endpoints the Aurelius frontend (apps/atlas) calls besides the Atlas v2 API."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Request, Response

from ..web.common import json_body, user_of

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
