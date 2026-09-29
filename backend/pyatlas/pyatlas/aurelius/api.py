"""/api/aurelius - endpoints the Aurelius frontend (apps/atlas) calls besides the Atlas v2 API."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Query, Request, Response
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


@router.get("/frontend-config")
async def frontend_config(request: Request):
    """``config.json`` of the frontend (served by the proxy as ``/<ns>/<tenant>/atlas/config.json``): the Keycloak
    realm and client of the request's tenant, so one frontend build serves every tenant.  Public (needed before
    the login); tells nothing beyond what the login page shows."""
    s = request.app.state.settings
    tenant = getattr(request.state, "tenant", None)
    realm = (tenant.record.get("realm") or tenant.id) if tenant is not None else s.frontend_realm
    body = {"keycloak": {"url": s.frontend_keycloak_url, "realm": realm, "clientId": s.frontend_client_id}}
    if tenant is not None:
        body["tenant"] = {"id": tenant.id, "name": tenant.name}
    return JSONResponse(body, headers={"Cache-Control": "no-cache"})


@router.get("/kibana-discover")
async def kibana_discover(request: Request, oidc_callback: str = "", target_link_uri: str = "",
                          method: str = "get", x_csrf: str = ""):
    """Discovery page of the proxy's Kibana login (mod_auth_openidc ``OIDCDiscoverURL``): chooses the Keycloak
    realm of the tenant in ``target_link_uri`` (``/<ns>/kibana/s/<tenant>/...`` or ``/<ns>/<tenant>/kibana/``) and
    sends the browser back to the callback with that realm's issuer.  Answers only relative redirects to the
    proxy's own callback path, so it cannot be used to send users elsewhere."""
    import re
    from urllib.parse import urlencode, urlsplit
    tenants = request.app.state.tenants
    s = request.app.state.settings
    target = urlsplit(target_link_uri or "")
    callback = urlsplit(oidc_callback or "")
    if tenants is None or not callback.path.endswith("/kibana-oidc/callback") or ".." in callback.path:
        return JSONResponse({"errorMessage": "bad request"}, status_code=400)
    if callback.netloc and target.netloc and callback.netloc != target.netloc:
        return JSONResponse({"errorMessage": "bad request"}, status_code=400)
    m = re.search(r"/kibana/s/([a-z0-9-]+)(?:/|$)", target.path) or re.search(r"/([a-z0-9-]+)/kibana(?:/|$)",
                                                                                 target.path)
    rec = await tenants.registry.get(m.group(1)) if m else None
    if m and m.group(1) == s.tenant_platform_realm:           # the operators' space
        rec = {"id": m.group(1), "realm": m.group(1), "status": "active"}
    if rec is None or rec.get("status") != "active":
        return JSONResponse({"errorMessage": "Open Kibana through the address of your organisation: "
                                             "/<namespace>/<organisation>/kibana/"}, status_code=404)
    realm = rec.get("realm") or rec["id"]
    issuers = [x.strip() for x in (s.tenant_oidc_issuers or "").split(",") if x.strip()]
    if not issuers:
        return JSONResponse({"errorMessage": "no issuer configured"}, status_code=500)
    query = urlencode({"iss": issuers[0].format(tenant=realm, realm=realm), "target_link_uri": target_link_uri,
                       "method": method, "x_csrf": x_csrf})
    return Response(status_code=302, headers={"Location": f"{callback.path}?{query}", "Cache-Control": "no-store"})


@router.post("/repository/log")
async def log_clickstream(request: Request):
    """Frontend clickstream event (``libs/repository`` ``logClickstreamEvent``: app, timestamp, url, userid).
    Logged with the authenticated user; the ``userid`` sent by the browser is not trusted."""
    body = await json_body(request, default={}) or {}
    event = {"type": "clickstream", "user": user_of(request), "app": _clip(body.get("app")),
             "url": _clip(body.get("url")), "timestamp": _clip(body.get("timestamp")) or int(time.time() * 1000)}
    clickstream_log.info(json.dumps(event))
    a = _aurelius(request)
    if a is not None and isinstance(event["url"], str):
        ts = body.get("timestamp") if isinstance(body.get("timestamp"), int) else None
        try:
            await a.clickstream.record(event["user"], event["app"], event["url"], ts)
        except Exception:  # noqa: BLE001 - never bother the frontend with analytics problems
            logging.getLogger("pyatlas.aurelius").exception("could not store a clickstream event")
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


def _require_read(request: Request, what: str) -> None:
    """Aurelius read endpoints (search documents, dashboard, lineage listing) need entity-read, like the Atlas
    entity API: a Keycloak user without an Aurelius role gets 403."""
    svc(request).authz.verify_entity(Privilege.ENTITY_READ, {"typeName": "m4i_referenceable", "attributes": {}},
                                     what)


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
    _require_read(request, "search the Aurelius documents")
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
    _require_read(request, "read the Aurelius documents")
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
    svc(request).authz.verify_admin(Privilege.ADMIN_AUDITS, "read the Aurelius index status")
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


# ------------------------------------------------------------------ quality (phase 3)
@router.post("/validate_entity")
@router.post("/validate_entity/")
async def validate_entity(request: Request):
    """Governance quality of an entity being edited (the editor's live check; formerly m4i-validate-entity).
    Body: ``{entity, referredEntities}``, a bare entity, or the editor's form value; answer per attribute."""
    from .gov_quality import validate
    a = _aurelius(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    body = await json_body(request, default={}) or {}
    if not isinstance(body, dict):
        return JSONResponse({"errors": ["expected an entity"]}, status_code=400)
    return validate(body, a.gov_rules, svc(request).typedefs.registry)


def _quality_admin(request: Request):
    a = _aurelius(request)
    if a is None:
        return None
    svc(request).authz.verify_admin(Privilege.ADMIN_IMPORT, "write data quality results")
    return a


@router.post("/quality/results")
async def post_quality_results(request: Request):
    """Data quality scores from the quality tooling (formerly the Kafka quality topics + propagate_quality):
    ``{"results": [{"quality": "<guid or qualifiedName of the m4i_data_quality>", "dqscore": 0.93,
    "businessRuleId": 43, "dataDomainName": "Finance"}]}`` (or the bare list; only ``quality`` and ``dqscore``
    are required).  Admin only."""
    a = _quality_admin(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    body = await json_body(request, default={})
    results = body.get("results") if isinstance(body, dict) else body
    if not isinstance(results, list):
        return JSONResponse({"errors": ["expected {\"results\": [...]}"]}, status_code=400)
    for i, r in enumerate(results):
        score = r.get("dqscore") if isinstance(r, dict) else None
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 1:
            return JSONResponse({"errors": [f"results[{i}]: dqscore must be a number between 0 and 1"]},
                                status_code=400)
    return await a.post_quality_results(results)


@router.delete("/quality/results")
async def delete_quality_results(request: Request, quality: list[str] = Query(default=[]), all: bool = False):
    """Remove the results of the given rules (``?quality=<guid or qualifiedName>``, repeatable) or ``?all=true``."""
    a = _quality_admin(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    if not quality and not all:
        return JSONResponse({"errors": ["name the rules with ?quality=... or pass ?all=true"]}, status_code=400)
    return await a.delete_quality_results(None if all else quality)


# ------------------------------------------------------------------ governance dashboard (phase 4)
@router.get("/data_governance_dashboard")
@router.get("/data_governance_dashboard/")
async def data_governance_dashboard(request: Request):
    """Data domains and whether they have a data dictionary (the frontend's ``getDashboard``; formerly the
    python-rest ``data_governance/dashboard``): ``{totalNumberOfDomains, totalNumberOfActiveDomains,
    domains: {<name>: {name, guid, isActive, totalNumberOfEntities}}}``; a domain is active once it has a data
    entity."""
    from .engines import SEARCH_DOCUMENTS
    a = _aurelius(request)
    if a is None:
        return JSONResponse({"errors": ["Aurelius is disabled"]}, status_code=404)
    _require_read(request, "read the governance dashboard")
    domains = {}
    async for _id, d in a.store.scan(a.index(SEARCH_DOCUMENTS), {"term": {"typename": "m4i_data_domain"}},
                                     sort_field="id"):
        n = len(d.get("deriveddataentityguid") or [])
        domains[d.get("name") or d["guid"]] = {"name": d.get("name"), "guid": d["guid"], "isActive": n > 0,
                                               "totalNumberOfEntities": n}
    return {"totalNumberOfDomains": len(domains),
            "totalNumberOfActiveDomains": sum(1 for x in domains.values() if x["isActive"]),
            "domains": dict(sorted(domains.items()))}


# ------------------------------------------------------------------ lineage registration API (phase 4)
lineage_router = APIRouter(prefix="/api/lin_api")


def _lin_namespace(namespace: str):
    from .lineage_api import NAMESPACES
    ns = namespace.strip("/")
    return ns if ns in NAMESPACES else None


def _unknown_namespace(namespace: str) -> JSONResponse:
    return JSONResponse({"message": f"The requested URL was not found on the server: {namespace}"}, status_code=404)


@lineage_router.get("/{namespace:path}")
async def lineage_api_get(namespace: str, request: Request):
    """Qualified names of all (active) entities of the namespace's type, subtypes included."""
    from .lineage_api import NAMESPACES
    ns = _lin_namespace(namespace)
    if ns is None:
        return _unknown_namespace(namespace)
    type_name = NAMESPACES[ns][0]
    _require_read(request, "list registered entities")
    s = svc(request)
    names, offset = [], 0
    while True:
        page = await s.search.basic({"typeName": type_name, "excludeDeletedEntities": True, "limit": 1000,
                                     "offset": offset})
        ents = page.get("entities") or []
        names += [(e.get("attributes") or {}).get("qualifiedName") for e in ents]
        if len(ents) < 1000:
            break
        offset += 1000
    return {"entities": len(names), "qualifiedNames": names}


@lineage_router.post("/{namespace:path}")
async def lineage_api_post(namespace: str, request: Request):
    """Registers one entity (see :mod:`.lineage_api`); ``{"CREATE": n, "UPDATE": n, "DELETE": n}``."""
    from .lineage_api import PayloadError, convert, mutation_counts
    ns = _lin_namespace(namespace)
    if ns is None:
        return _unknown_namespace(namespace)
    body = await json_body(request, default=None)
    try:
        entities, referred = convert(ns, body)
    except PayloadError as e:
        return JSONResponse({"errors": e.errors, "message": "Input payload validation failed"}, status_code=400)
    s = svc(request)
    result = await s.entities.create_or_update({"entities": entities, "referredEntities": referred},
                                               user_of(request))
    return mutation_counts(result)
