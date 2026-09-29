"""/api/atlas/v2/glossary (Atlas ``GlossaryREST``)."""
from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Dict, List

from fastapi import APIRouter, Request, Response, UploadFile
from fastapi.responses import FileResponse

from ..errors import AtlasBaseException, AtlasErrorCode
from ..glossary.service import IMPORT_HEADERS, read_tabular_file, write_tabular_file
from .common import json_body, svc, user_of

router = APIRouter(prefix="/api/atlas/v2/glossary")
KIND = "glossary_export_downloads"


def _g(request: Request):
    return svc(request).glossary


def _page(request: Request):
    q = request.query_params
    return int(q.get("limit", -1)), int(q.get("offset", 0)), q.get("sort", "ASC")


# ------------------------------------------------------------------ fixed paths first (before /{glossaryGuid})
@router.get("")
async def get_glossaries(request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_glossaries(limit, offset, sort)


@router.post("")
async def create_glossary(request: Request):
    return await _g(request).create_glossary(await json_body(request), user_of(request))


@router.get("/import/template")
async def import_template():
    return Response(content=", ".join(IMPORT_HEADERS), media_type="application/octet-stream",
                    headers={"Content-Disposition": "attachment; filename=template_business_glossary"})


@router.post("/import")
async def import_glossary(request: Request, file: UploadFile):
    rows = read_tabular_file(file.filename or "", await file.read())
    return await _g(request).import_terms(rows, user_of(request))


@router.post("/search")
async def search_glossary(request: Request):
    return await _g(request).search(await json_body(request, default={}))


async def _create_export(request: Request):
    s = svc(request)
    params = s.glossary.export_parameters(await json_body(request, default={}))
    user = user_of(request)
    ts = params.get("exportTimestamp") or _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # the client's value becomes part of a file name: no path separators or dots (path traversal)
    ts = re.sub(r"[^A-Za-z0-9_\-]", "_", str(ts))[:40]
    file_name = f"{user}_GLOSSARY_EXPORT_{ts}.{'xlsx' if params['format'] == 'XLSX' else 'csv'}"

    async def writer(path):
        headers, data = await s.glossary.export_rows(params)
        write_tabular_file(path, params["format"], headers, data)
    s.downloads.submit(KIND, user, file_name, writer)
    return Response(status_code=204)


@router.post("/download/create_file")
async def export_create_file(request: Request):
    return await _create_export(request)


@router.post("/create_file")
async def export_create_file_alias(request: Request):
    return await _create_export(request)


@router.get("/download/status")
async def export_status(request: Request):
    return svc(request).downloads.status(KIND, user_of(request))


@router.get("/download/{filename}")
async def export_download(filename: str, request: Request):
    path = svc(request).downloads.resolve(KIND, user_of(request), filename)
    if not path.is_file():
        return Response(status_code=204)
    return FileResponse(path, media_type="application/octet-stream", filename=path.name)


# ------------------------------------------------------------------ terms
@router.post("/term")
async def create_term(request: Request):
    return await _g(request).create_term(await json_body(request), user_of(request))


@router.post("/terms")
async def create_terms(request: Request):
    return await _g(request).create_terms(await json_body(request), user_of(request))


@router.get("/term/{guid}")
async def get_term(guid: str, request: Request):
    return await _g(request).get_term(guid)


@router.put("/term/{guid}")
async def update_term(guid: str, request: Request):
    return await _g(request).update_term(guid, await json_body(request), user_of(request))


@router.put("/term/{guid}/partial")
async def partial_update_term(guid: str, request: Request):
    return await _g(request).partial_update_term(guid, await json_body(request), user_of(request))


@router.delete("/term/{guid}", status_code=204)
async def delete_term(guid: str, request: Request):
    await _g(request).delete_term(guid, user_of(request))
    return Response(status_code=204)


@router.get("/terms/{guid}/related")
async def related_terms(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_related_terms(guid, limit, offset, sort)


@router.get("/terms/{guid}/assignedEntities")
async def assigned_entities(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_assigned_entities(guid, limit, offset, sort)


@router.post("/terms/{guid}/assignedEntities", status_code=204)
async def assign_term(guid: str, request: Request):
    await _g(request).assign_term(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.delete("/terms/{guid}/assignedEntities", status_code=204)
async def remove_assignment(guid: str, request: Request):
    await _g(request).remove_term_assignment(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


@router.put("/terms/{guid}/assignedEntities", status_code=204)
async def disassociate(guid: str, request: Request):
    await _g(request).remove_term_assignment(guid, await json_body(request), user_of(request))
    return Response(status_code=204)


# ------------------------------------------------------------------ categories
@router.post("/category")
async def create_category(request: Request):
    return await _g(request).create_category(await json_body(request), user_of(request))


@router.post("/categories")
async def create_categories(request: Request):
    return await _g(request).create_categories(await json_body(request), user_of(request))


@router.get("/category/{guid}")
async def get_category(guid: str, request: Request):
    return await _g(request).get_category(guid)


@router.put("/category/{guid}")
async def update_category(guid: str, request: Request):
    return await _g(request).update_category(guid, await json_body(request), user_of(request))


@router.put("/category/{guid}/partial")
async def partial_update_category(guid: str, request: Request):
    return await _g(request).partial_update_category(guid, await json_body(request), user_of(request))


@router.delete("/category/{guid}", status_code=204)
async def delete_category(guid: str, request: Request):
    await _g(request).delete_category(guid, user_of(request))
    return Response(status_code=204)


@router.get("/category/{guid}/related")
async def related_categories(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_related_categories(guid, limit, offset, sort)


@router.get("/category/{guid}/terms")
async def category_terms(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_category_terms(guid, limit, offset, sort)


# ------------------------------------------------------------------ glossary by guid
@router.get("/{guid}")
async def get_glossary(guid: str, request: Request):
    return await _g(request).get_glossary(guid)


@router.get("/{guid}/detailed")
async def get_detailed(guid: str, request: Request):
    return await _g(request).get_detailed_glossary(guid)


@router.put("/{guid}")
async def update_glossary(guid: str, request: Request):
    return await _g(request).update_glossary(guid, await json_body(request), user_of(request))


@router.put("/{guid}/partial")
async def partial_update_glossary(guid: str, request: Request):
    return await _g(request).partial_update_glossary(guid, await json_body(request), user_of(request))


@router.delete("/{guid}", status_code=204)
async def delete_glossary(guid: str, request: Request):
    await _g(request).delete_glossary(guid, user_of(request))
    return Response(status_code=204)


@router.get("/{guid}/terms")
async def glossary_terms(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_glossary_terms(guid, limit, offset, sort)


@router.get("/{guid}/terms/headers")
async def glossary_term_headers(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_glossary_term_headers(guid, limit, offset, sort)


@router.get("/{guid}/categories")
async def glossary_categories(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_glossary_categories(guid, limit, offset, sort)


@router.get("/{guid}/categories/headers")
async def glossary_category_headers(guid: str, request: Request):
    limit, offset, sort = _page(request)
    return await _g(request).get_glossary_category_headers(guid, limit, offset, sort)
