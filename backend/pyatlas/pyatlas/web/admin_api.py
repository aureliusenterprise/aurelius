"""/api/atlas/admin (Atlas ``AdminResource``) and /api/atlas/v2/indexrecovery (``IndexRecoveryREST``)."""
from __future__ import annotations

import datetime as _dt
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import PlainTextResponse

from ..admin.service import ageout_audits, check_state, now_ms, reindex, thread_dump
from ..auth import csrf_token
from ..authz import Privilege
from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import entity_header
from .common import json_body, svc, user_of

router = APIRouter(prefix="/api/atlas/admin")
recovery_router = APIRouter(prefix="/api/atlas/v2/indexrecovery")

TIMEZONES = ["UTC", "Europe/Amsterdam", "Europe/London", "Europe/Berlin", "America/New_York", "America/Chicago",
             "America/Los_Angeles", "Asia/Kolkata", "Asia/Shanghai", "Asia/Tokyo", "Australia/Sydney"]


def _verify_admin(request: Request, privilege: str, message: str) -> None:
    svc(request).authz.verify_admin(privilege, message)


def _client(request: Request) -> str:
    return request.client.host if request.client else ""


# ------------------------------------------------------------------ server info
@router.get("/version")
async def version(request: Request):
    s = request.app.state.settings
    return {"Version": s.version, "Revision": "pyatlas", "Name": "apache-atlas",
            "Description": "Metadata Management and Data Governance Platform (Python / Elasticsearch implementation)"}


@router.get("/status")
async def status(request: Request):
    return {"Status": "ACTIVE"}


@router.get("/liveness")
async def liveness():
    return Response(status_code=200)


@router.get("/readiness")
async def readiness(request: Request):
    try:
        ok = await request.app.state.es.ping()
    except Exception:
        ok = False
    return Response(status_code=200 if ok is not False else 503)


@router.get("/session")
async def session(request: Request):
    s = request.app.state.settings
    u = getattr(request.state, "user", None)
    data: Dict[str, Any] = {
        "atlas.rest-csrf.enabled": s.csrf_enabled,
        "atlas.rest-csrf.browser-useragents-regex": "^Mozilla.*,^Opera.*,^Chrome.*",
        "atlas.rest-csrf.methods-to-ignore": "GET,OPTIONS,HEAD,TRACE",
        "atlas.rest-csrf.custom-header": "X-XSRF-HEADER",
        "atlas.entity.update.allowed": svc(request).authz.is_entity_allowed(Privilege.ENTITY_UPDATE),
        "atlas.entity.create.allowed": svc(request).authz.is_entity_allowed(Privilege.ENTITY_CREATE),
        "atlas.ui.editable.entity.types": "hdfs_path",
        "atlas.ui.default.version": s.default_ui,
        "userName": u.name if u else None,
        "groups": sorted(u.groups) if u else [],
        "timezones": TIMEZONES,
        "atlas.ui.date.timezone.format.enabled": True,
        "atlas.ui.date.format": "MM/DD/YYYY hh:mm:ss A",
        "atlas.debug.metrics.enabled": True,
        "atlas.tasks.enabled": False,
        "atlas.tasks.ui.tab.enabled": False,
        "atlas.lineage.on.demand.enabled": s.lineage_on_demand_enabled,
        "atlas.lineage.on.demand.default.node.count": s.lineage_on_demand_default_node_count,
        "atlas.relationship.search.enabled": True,
        "_csrfToken": csrf_token(request),
    }
    if s.session_timeout_secs and s.session_timeout_secs > 0:
        data["atlas.session.timeout.secs"] = s.session_timeout_secs
    return data


@router.get("/stack")
async def stack(request: Request):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "thread dump")
    return PlainTextResponse(thread_dump())


@router.get("/debug/metrics")
async def debug_metrics(request: Request):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "debug metrics")
    return svc(request).request_metrics.report()


@router.get("/server/{server_name}")
async def server(server_name: str, request: Request):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "get server")
    s = svc(request)
    reg = s.typedefs.registry
    if "AtlasServer" not in reg.entities:
        raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, "AtlasServer")
    q = {"bool": {"filter": [{"term": {"typeName": "AtlasServer"}}, {"term": {"status": "ACTIVE"}}],
                  "should": [{"term": {"idx.str.name": server_name}}, {"term": {"idx.str.qualifiedName": server_name}},
                             {"term": {"idx.str.fullName": server_name}}], "minimum_should_match": 1}}
    r = await s.store.search(s.store.entities, q, size=1)
    hits = r["hits"]["hits"]
    if not hits:
        raise AtlasBaseException(AtlasErrorCode.INSTANCE_BY_UNIQUE_ATTRIBUTE_NOT_FOUND, "AtlasServer", server_name)
    a = hits[0]["_source"].get("attributes") or {}
    return {"guid": hits[0]["_id"], "name": a.get("name"), "fullName": a.get("fullName") or a.get("qualifiedName"),
            "displayName": a.get("displayName"), "additionalInfo": a.get("additionalInfo") or {},
            "urls": a.get("urls") or []}


# ------------------------------------------------------------------ metrics
@router.get("/metrics")
async def metrics(request: Request, excludeTypeAndSubTypeEntity: bool = True):
    return await svc(request).metrics()


@router.get("/metricsstats")
async def metrics_stats(request: Request, mininfo: bool = True):
    return await svc(request).metrics_stats.all(mininfo)


@router.get("/metricsstat/{collection_time}")
async def metrics_stat(collection_time: str, request: Request):
    return await svc(request).metrics_stats.by_time(collection_time)


def _range_params(request: Request):
    q = request.query_params
    if not q.get("startTime") or not q.get("endTime"):
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "startTime or endTime is null/empty.")
    return int(q["startTime"]), int(q["endTime"]), q.getlist("typeName")


@router.get("/metricsstats/range")
async def metrics_range(request: Request):
    st, et, types = _range_params(request)
    return await svc(request).metrics_stats.range(st, et, types)


@router.get("/metricsstats/charts")
async def metrics_charts(request: Request):
    s = svc(request)
    q = request.query_params
    types = q.getlist("typeName")
    if not q.get("startTime") or not q.get("endTime"):
        # no range given: current counts as a single data point
        m = (await s.metrics())["data"]["entity"]
        now = now_ms()
        return {t: [{"key": label, "values": [[now, int(m[key].get(t, 0))]]}
                    for label, key in (("Active", "entityActive"), ("Deleted", "entityDeleted"), ("Shell", "entityShell"))]
                for t in types}
    st, et, types = _range_params(request)
    return await s.metrics_stats.charts(st, et, types)


# ------------------------------------------------------------------ audits
@router.post("/audits")
async def audits(request: Request):
    _verify_admin(request, Privilege.ADMIN_AUDITS, "Admin Audits")
    return await svc(request).audits.search(await json_body(request, default={}))


@router.post("/audits/ageout")
async def audits_ageout(request: Request, useAuditConfig: bool = False):
    _verify_admin(request, Privilege.ADMIN_AUDITS, "Admin Audits Ageout")
    c = await json_body(request, default={})
    s = svc(request)
    if useAuditConfig:
        c = {"auditAgingEnabled": True, "defaultAgeoutEnabled": True,
             "defaultAgeoutTTLInDays": s.settings.audit_ageout_ttl_days,
             "defaultAgeoutAuditCount": s.settings.audit_ageout_count}
    if not c.get("auditAgingEnabled"):
        return None
    return await ageout_audits(s, c, user_of(request))


@router.get("/audit/{audit_guid}/details")
async def audit_details(audit_guid: str, request: Request, limit: int = 10, offset: int = 0):
    _verify_admin(request, Privilege.ADMIN_AUDITS, "audit details")
    s = svc(request)
    e = await s.audits.get(audit_guid)
    if e is None:
        return []
    guids: List[str] = []
    if e.get("auditRowKind") == "SUMMARY":
        for b in await s.audits.search({"auditFilters": {"attributeName": "runId", "operator": "eq",
                                                         "attributeValue": e.get("runId")}}):
            if b.get("auditRowKind") == "BATCH" and b.get("result"):
                guids += b["result"].split(",")
    elif e.get("result") and not str(e["result"]).startswith("{"):
        guids = e["result"].split(",")
    guids = guids[offset:offset + limit]
    docs = await s.store.mget(s.store.entities, guids)
    out = []
    for g in guids:
        if g in docs:
            out.append(entity_header(s.typedefs.registry, docs[g]))
        else:
            ev = await s.entities.audit.list_events(g, count=1, action="ENTITY_PURGE")
            if ev:
                try:
                    out.append(json.loads(ev[0]["details"].split(": ", 1)[1]))
                except (IndexError, ValueError):
                    pass
    return out


async def _purge_audit(request: Request, audit_guid: str) -> dict:
    e = await svc(request).audits.get(audit_guid)
    if e is None or e.get("operation") not in ("PURGE", "AUTO_PURGE"):
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, f"Not a purge audit entry: {audit_guid}")
    if e.get("auditRowKind") != "SUMMARY":
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, f"Not a purge summary audit entry: {audit_guid}")
    return e


@router.get("/audit/{audit_guid}/summary")
async def audit_summary(audit_guid: str, request: Request):
    _verify_admin(request, Privilege.ADMIN_AUDITS, "Admin Audits")
    e = await _purge_audit(request, audit_guid)
    try:
        return json.loads(e["result"])
    except (TypeError, ValueError):
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, f"No purge summary for audit: {audit_guid}")


@router.get("/audit/{audit_guid}/batches")
async def audit_batches(audit_guid: str, request: Request):
    _verify_admin(request, Privilege.ADMIN_AUDITS, "Admin Audits")
    e = await _purge_audit(request, audit_guid)
    rows = await svc(request).audits.search({"auditFilters": {"attributeName": "runId", "operator": "eq",
                                                              "attributeValue": e.get("runId")}})
    return [b["guid"] for b in rows if b.get("auditRowKind") == "BATCH"]


@router.get("/expimp/audit")
async def expimp_audit(request: Request, serverName: Optional[str] = None, userName: Optional[str] = None,
                       operation: Optional[str] = None, startTime: Optional[str] = None,
                       endTime: Optional[str] = None, limit: int = 0, offset: int = 0):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "export import audit")
    return await svc(request).audits.expimp(userName, operation, serverName, startTime, endTime, limit, offset)


# ------------------------------------------------------------------ purge
@router.put("/purge")
async def purge(request: Request):
    _verify_admin(request, Privilege.ADMIN_PURGE, "purge entity")
    s = svc(request)
    guids = list(await json_body(request) or [])
    start = now_ms()
    res = await s.entities.purge(guids, user_of(request))
    purged = [h["guid"] for h in (res.get("mutatedEntities") or {}).get("PURGE", [])]
    run_id = str(uuid.uuid4())
    skipped = len(set(guids) - set(purged))
    summary = {"requestedCount": len(guids), "purgedCount": len(purged), "purgedDependenciesCount": 0,
               "failedCount": 0, "failedDependenciesCount": 0, "skippedCount": skipped,
               "validGuidCount": len(purged), "executionFailed": False, "expandedEntityCount": len(purged),
               "skippedRequestedCount": skipped, "skippedDependenciesCount": 0,
               "unprocessedCount": 0, "batchCount": 1 if purged else 0, "runId": run_id}
    end = now_ms()
    await s.audits.add("PURGE", user_of(request), str(guids), json.dumps(summary), len(purged), start, end,
                       _client(request), run_id=run_id, row_kind="SUMMARY")
    if purged:
        await s.audits.add("PURGE", user_of(request), str(guids), ",".join(purged), len(purged), start, end,
                           _client(request), run_id=run_id, row_kind="BATCH")
    res["summary"] = summary
    return res


# ------------------------------------------------------------------ export / import
@router.post("/export")
async def export(request: Request):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "export")
    s = svc(request)
    body = await json_body(request)
    async with s.impexp.lock:
        data, result = await s.impexp.export(body, user_of(request), _client(request))
    if not any(k.startswith("entity:") for k in result.get("metrics", {})) and body.get("omitZipResponseForEmptyExport"):
        return Response(status_code=204)
    return Response(content=data, media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=AtlasExportResult"})


async def _multipart_import(request: Request):
    form = await request.form()
    raw = form.get("request") or "{}"
    req = json.loads(raw if isinstance(raw, str) else ((await raw.read()).decode("utf-8") or "{}"))
    data = form.get("data")
    if data is None:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "multipart field 'data' (zip) is required")
    return req, (await data.read()) if hasattr(data, "read") else str(data).encode()


@router.post("/import")
async def import_data(request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "importData")
    s = svc(request)
    req, data = await _multipart_import(request)
    if not data:
        return {}
    async with s.impexp.lock:
        return await s.impexp.import_zip(data, req, user_of(request), _client(request))


@router.post("/importfile")
async def import_file(request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "importFile")
    s = svc(request)
    req = await json_body(request)
    fname = (req.get("options") or {}).get("fileName")
    if not fname:
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, "fileName option is required")
    # only files below PYATLAS_IMPORT_DIR can be imported (no reading of arbitrary server files)
    base = Path(s.settings.import_dir).resolve()
    target = Path(fname) if Path(fname).is_absolute() else base / fname
    try:
        target = target.resolve()
    except OSError:
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, f"cannot read {fname}")
    if base not in target.parents or not target.is_file():
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS,
                                 f"cannot read {fname}: only files in the import directory can be imported")
    if target.stat().st_size > s.settings.max_upload_mb * 1024 * 1024:
        raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, f"{fname} is too large")
    data = target.read_bytes()
    async with s.impexp.lock:
        return await s.impexp.import_zip(data, req, user_of(request), _client(request))


@router.post("/async/import")
async def async_import(request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "asyncImportData")
    s = svc(request)
    req, data = await _multipart_import(request)
    if not data:
        return {}
    return await s.async_imports.submit(data, req, user_of(request), _client(request))


@router.get("/async/import/status")
async def async_import_status(request: Request, offset: int = 0, limit: int = 50):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "async import status")
    return await svc(request).async_imports.list(offset, limit)


@router.get("/async/import/status/{import_id}")
async def async_import_status_by_id(import_id: str, request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "async import status by id")
    return await svc(request).async_imports.get(import_id)


@router.delete("/async/import/{import_id}", status_code=204)
async def async_import_abort(import_id: str, request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "abort async import")
    await svc(request).async_imports.abort(import_id)
    return Response(status_code=204)


# ------------------------------------------------------------------ misc
@router.post("/checkstate")
async def checkstate(request: Request):
    svc(request).authz.verify_entity(Privilege.ENTITY_READ, None, "check state")
    return await check_state(svc(request), await json_body(request, default={}))


@router.get("/patches")
async def patches(request: Request):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "patches")
    s = svc(request)
    doc = await s.store.get(s.store.meta, "typedef_patches")
    value = (doc or {}).get("value") or {}
    applied = value.get("applied", {})
    details = value.get("details", {})
    out = []
    for pid, st in sorted(applied.items()):
        d = details.get(pid, {})
        out.append({"id": pid, "description": d.get("description"), "type": "TYPEDEF_PATCH", "action": d.get("action"),
                    "updatedBy": "admin", "createdBy": "admin", "createdTime": d.get("time", 0),
                    "updatedTime": d.get("time", 0), "status": st})
    return {"patches": out}


def _task_view(t: dict) -> dict:
    return {"type": t.get("kind"), "guid": t["guid"], "createdBy": t.get("createdBy"), "createdTime": t.get("createdTime"),
            "updatedTime": t.get("startTime") or t.get("createdTime"), "startTime": t.get("startTime"),
            "endTime": None, "parameters": {"fileName": t.get("fileName")}, "attemptCount": 1,
            "errorMessage": None, "status": t.get("status")}


@router.get("/tasks")
async def tasks(request: Request, guids: List[str] = Query(default=[])):
    _verify_admin(request, Privilege.ADMIN_PURGE, "tasks")
    s = svc(request)
    out = [_task_view(t) for t in s.downloads.tasks.values()]
    if guids:
        out = [t for t in out if t["guid"] in guids]
    return out + await s.tasks.list(guids or None)


@router.delete("/tasks", status_code=204)
async def delete_tasks(request: Request, guids: List[str] = Query(default=[])):
    _verify_admin(request, Privilege.ADMIN_PURGE, "delete tasks")
    s = svc(request)
    for g in guids:
        s.downloads.tasks.pop(g, None)
    if guids:
        await s.tasks.delete(guids)
    return Response(status_code=204)


@router.get("/activeSearches")
async def active_searches(request: Request):
    _verify_admin(request, Privilege.ADMIN_EXPORT, "active searches")
    return svc(request).active_searches.list()


@router.delete("/activeSearches/{search_id}")
async def terminate_search(search_id: str, request: Request):
    s = svc(request)
    if not s.authz.is_admin_allowed(Privilege.ADMIN_EXPORT):
        owner = s.active_searches.owner(search_id)
        if owner is None:
            return False
        if owner != user_of(request):
            _verify_admin(request, Privilege.ADMIN_EXPORT, "terminate active search")
    return s.active_searches.terminate(search_id)


# ------------------------------------------------------------------ index recovery
def _iso(ms: Optional[int]) -> str:
    if not ms:
        return "Not applicable"
    return _dt.datetime.fromtimestamp(ms / 1000, _dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@recovery_router.get("")
async def recovery_info(request: Request):
    s = svc(request)
    doc = await s.store.get(s.store.meta, "index_recovery")
    v = (doc or {}).get("value") or {}
    return {"startTime": _iso(v.get("startTime")), "prevTime": _iso(v.get("prevTime")),
            "customTime": _iso(v.get("customTime"))}


@recovery_router.post("/start", status_code=204)
async def recovery_start(request: Request, startTime: Optional[str] = None):
    _verify_admin(request, Privilege.ADMIN_IMPORT, "to start dynamic index recovery by custom time")
    s = svc(request)
    if not startTime:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "Index Recovery requested without start time")
    try:
        ms = int(_dt.datetime.fromisoformat(startTime.replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"invalid startTime {startTime}")
    doc = await s.store.get(s.store.meta, "index_recovery")
    prev = ((doc or {}).get("value") or {}).get("startTime")
    now = now_ms()
    await s.store.put(s.store.meta, "index_recovery", {"kind": "system", "name": "index_recovery", "updateTime": now,
                                                        "value": {"startTime": now, "prevTime": prev, "customTime": ms}})
    await reindex(s, ms)
    return Response(status_code=204)
