"""Shared helpers for the REST layer."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from fastapi import Request

from ..errors import AtlasBaseException, AtlasErrorCode

_ATTR_N = re.compile(r"^attr_(\d+):(.+)$")


def user_of(request: Request) -> str:
    u = getattr(request.state, "user", None)
    return u.name if u is not None else "anonymous"


def svc(request: Request):
    return request.app.state.services


def qbool(v: Any, default: bool = False) -> bool:
    if v is None:
        return default
    return str(v).lower() in ("true", "1", "yes")


def unique_attrs_from_query(request: Request) -> Dict[str, Any]:
    out = {}
    for k, v in request.query_params.multi_items():
        if k.startswith("attr:"):
            out[k[5:]] = v
    return out


def bulk_unique_attrs_from_query(request: Request) -> List[Dict[str, Any]]:
    groups: Dict[int, Dict[str, Any]] = {}
    for k, v in request.query_params.multi_items():
        m = _ATTR_N.match(k)
        if m:
            groups.setdefault(int(m.group(1)), {})[m.group(2)] = v
    return [groups[i] for i in sorted(groups)]


async def json_body(request: Request, default: Any = None) -> Any:
    limit = getattr(getattr(request.app.state, "settings", None), "max_json_mb", 32) * 1024 * 1024
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"JSON body larger than {limit // (1024 * 1024)} MB")
    raw = await request.body()
    if len(raw) > limit:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"JSON body larger than {limit // (1024 * 1024)} MB")
    if not raw:
        if default is not None:
            return default
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "request body is required")
    try:
        return json.loads(raw)
    except ValueError as e:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"invalid JSON: {e}")
