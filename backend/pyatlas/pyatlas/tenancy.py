"""Multi-tenancy: one pyatlas process serves several tenants, each with its own data, realm and background jobs.

A tenant is a customer organisation.  It has

* an id (``acme``): the path segment of its URLs (``/aurelius/acme/atlas/``), the name of its Keycloak realm and
  part of its index names (``aurelius_acme_entities``, ...),
* an entry in the tenant registry (index ``aurelius_platform_tenants``): name, status, optional Elasticsearch API
  key that can only reach the tenant's indices,
* a *tenant context*: a complete :class:`~pyatlas.services.Services` (store with the tenant's index prefix, type
  registry, search, lineage, Aurelius documents, audits, downloads, jobs) plus the token validation of its realm.

The reverse proxy takes the tenant from the URL path and passes it in ``X-Aurelius-Tenant``; pyatlas believes this
header only from the trusted proxies (``PYATLAS_TRUSTED_PROXIES``) and answers everything else with 400.  Every
request then runs inside exactly one tenant context: :func:`pyatlas.web.common.svc` returns the context's services,
there is no code path from one context to another tenant's store.

Contexts are started on first use and stopped after ``PYATLAS_TENANT_IDLE_SECS`` without requests.  Personal-data
retention runs for every active tenant, loaded or not.
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any, Dict, List, Optional

from .config import Settings

log = logging.getLogger("pyatlas.tenancy")

TENANT_ID = re.compile(r"^[a-z][a-z0-9-]{1,30}[a-z0-9]$")
# path segments under /aurelius/ that are not tenants
RESERVED = {"auth", "platform", "atlas", "atlas2", "lin_api", "kibana", "api", "static", "admin", "default",
            "master", "assets", "health"}
ACTIVE = "active"
STATUSES = ("provisioning", ACTIVE, "suspended", "deleting")

REGISTRY_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"}, "name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "status": {"type": "keyword"}, "realm": {"type": "keyword"},
        # Keycloak's internal id of the realm (= tenant id for realms created by aurelius-admin); login events name it
        "realmId": {"type": "keyword"},
        "createdAt": {"type": "date", "format": "epoch_millis"},
        "updatedAt": {"type": "date", "format": "epoch_millis"},
        "retentionDays": {"type": "integer"},
        # Elasticsearch API key (base64 "id:key") limited to aurelius_<tenant>_*; not indexed
        "esApiKey": {"type": "keyword", "index": False, "doc_values": False},
        "esApiKeyId": {"type": "keyword"},
        "kibanaApiKeyId": {"type": "keyword"},
    },
}


class TenantError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def valid_tenant_id(tenant: str) -> bool:
    return bool(tenant) and TENANT_ID.match(tenant) is not None and tenant not in RESERVED


def check_tenant_id(tenant: str) -> str:
    if not valid_tenant_id(tenant):
        raise ValueError(f"invalid tenant id {tenant!r}: 3-32 characters a-z, 0-9 and '-', starting with a "
                         f"letter; not one of {', '.join(sorted(RESERVED))}")
    return tenant


def index_prefix(settings: Settings, tenant: str) -> str:
    return settings.tenant_index_prefix.format(tenant=tenant)


def tenant_settings(settings: Settings, tenant: str, default: bool = False) -> Settings:
    """The settings of one tenant context: its index prefix, its own download folder, its realm."""
    update: Dict[str, Any] = {
        "es_index_prefix": index_prefix(settings, tenant),
        "download_dir": settings.download_dir / tenant,
        "import_dir": settings.import_dir / tenant,
    }
    if not default:
        # sample data / quality seeds of the installation go to the default tenant only
        update.update(import_on_start="", aurelius_quality_seed="")
    return settings.model_copy(update=update)


def _split(value: str) -> List[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


class Tenant:
    """A loaded tenant context."""

    def __init__(self, tenant_id: str, record: dict, services, oidc, password_auth, client, own_client: bool):
        self.id = tenant_id
        self.record = record
        self.services = services
        self.oidc = oidc
        self.password_auth = password_auth
        self.client = client
        self.own_client = own_client
        self.last_used = time.monotonic()
        self.in_flight = 0

    @property
    def name(self) -> str:
        return self.record.get("name") or self.id


class TenantRegistry:
    """Tenant records in ``<platform prefix>_tenants`` (cached for a few seconds)."""

    def __init__(self, client, settings: Settings, cache_secs: float = 10.0):
        self.es = client
        self.index = f"{settings.tenant_platform_prefix}_tenants"
        self.settings = settings
        self.cache_secs = cache_secs
        self._cache: Dict[str, tuple] = {}

    async def bootstrap(self) -> None:
        """Creates the registry index when missing (development).  With Elasticsearch security pyatlas may only read
        it; "aurelius-admin platform init" creates it then."""
        try:
            if await self.es.indices.exists(index=self.index):
                return
            log.info("creating tenant registry %s", self.index)
            await self.es.indices.create(index=self.index, mappings=REGISTRY_MAPPING,
                                         settings={"number_of_shards": 1,
                                                   "number_of_replicas": self.settings.es_replicas})
        except Exception as e:  # noqa: BLE001 - e.g. 403: tenants appear once the registry exists
            log.warning("tenant registry %s not available (%s); run aurelius-admin platform init", self.index, e)

    async def get(self, tenant: str, cached: bool = True) -> Optional[dict]:
        now = time.monotonic()
        hit = self._cache.get(tenant)
        if cached and hit is not None and now - hit[1] < self.cache_secs:
            return hit[0]
        from elasticsearch import NotFoundError
        try:
            r = await self.es.get(index=self.index, id=tenant)
            doc = r["_source"]
        except NotFoundError:          # no such tenant, or no registry yet
            doc = None
        if len(self._cache) > 10000:
            self._cache.clear()
        self._cache[tenant] = (doc, now)
        return doc

    async def list(self) -> List[dict]:
        r = await self.es.search(index=self.index, query={"match_all": {}}, size=10000, sort=[{"id": "asc"}])
        return [h["_source"] for h in r["hits"]["hits"]]

    async def put(self, record: dict) -> dict:
        check_tenant_id(record["id"])
        if record.get("status", ACTIVE) not in STATUSES:
            raise ValueError(f"unknown tenant status {record.get('status')!r}")
        now = int(time.time() * 1000)
        doc = {"status": ACTIVE, "realm": record["id"], "name": record["id"], "createdAt": now, **record,
               "updatedAt": now}
        await self.es.index(index=self.index, id=doc["id"], document=doc, refresh="wait_for")
        self._cache.pop(doc["id"], None)
        return doc

    async def update(self, tenant: str, **fields) -> dict:
        doc = await self.get(tenant, cached=False)
        if doc is None:
            raise KeyError(tenant)
        return await self.put({**doc, **fields})

    async def delete(self, tenant: str) -> None:
        from elasticsearch import NotFoundError
        try:
            await self.es.delete(index=self.index, id=tenant, refresh="wait_for")
        except NotFoundError:
            pass
        self._cache.pop(tenant, None)


class TenantManager:
    def __init__(self, client, settings: Settings):
        self.client = client
        self.settings = settings
        self.registry = TenantRegistry(client, settings)
        self.default = settings.tenant_default or None
        self._tenants: Dict[str, Tenant] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._tasks: List[asyncio.Task] = []

    # ------------------------------------------------------------------ life cycle
    async def start(self) -> None:
        await self.registry.bootstrap()
        for tid in _split(self.settings.tenant_bootstrap):
            if await self.registry.get(tid, cached=False) is None:
                log.info("registering tenant %s (PYATLAS_TENANT_BOOTSTRAP)", tid)
                await self.registry.put({"id": check_tenant_id(tid), "name": tid, "status": ACTIVE})
        if self.default:
            try:
                await self.get(self.default)            # sample data, quality seeds: at start-up as before
            except TenantError as e:
                log.warning("default tenant %s not available: %s", self.default, e.message)
        loop = asyncio.get_running_loop()
        self._tasks = [loop.create_task(self._evict_loop()), loop.create_task(self._retention_loop())]

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        for tid in list(self._tenants):
            await self._unload(tid)

    @property
    def loaded(self) -> List[str]:
        return sorted(self._tenants)

    # ------------------------------------------------------------------ contexts
    async def get(self, tenant_id: str) -> Tenant:
        """The context of an active tenant, started on first use; 404 for unknown or inactive tenants."""
        t = self._tenants.get(tenant_id)
        if t is not None:
            rec = await self.registry.get(tenant_id)
            if rec is None or rec.get("status") != ACTIVE:
                await self._unload(tenant_id)
                raise TenantError(404, f"unknown tenant {tenant_id}")
            t.last_used = time.monotonic()
            return t
        if not valid_tenant_id(tenant_id):
            raise TenantError(404, "unknown tenant")
        lock = self._locks.setdefault(tenant_id, asyncio.Lock())
        async with lock:
            t = self._tenants.get(tenant_id)
            if t is not None:
                return t
            rec = await self.registry.get(tenant_id, cached=False)
            if rec is None or rec.get("status") != ACTIVE:
                raise TenantError(404, f"unknown tenant {tenant_id}")
            t = await self._load(tenant_id, rec)
            self._tenants[tenant_id] = t
            return t

    async def _load(self, tenant_id: str, rec: dict) -> Tenant:
        from .services import Services
        t0 = time.time()
        settings = tenant_settings(self.settings, tenant_id, default=tenant_id == self.default)
        client, own = self.client, False
        if rec.get("esApiKey") and not self.settings.in_memory:
            from .store.es import make_client
            client = make_client(settings.model_copy(update={"es_api_key": rec["esApiKey"], "es_username": None}))
            own = True
        elif self.settings.tenant_require_es_key and not self.settings.in_memory:
            raise TenantError(503, f"tenant {tenant_id} has no Elasticsearch API key")
        services = Services(client, settings, tenant=tenant_id)
        from .logctx import tenant_var
        token = tenant_var.set(tenant_id)       # jobs started now (rebuilds, metrics) log with the tenant
        try:
            await services.start(retention=False)
        except BaseException:
            try:
                await services.stop()
            except Exception:  # noqa: BLE001 - report the start failure
                log.debug("stopping the half-started tenant %s failed", tenant_id, exc_info=True)
            if own:
                await client.close()
            raise
        finally:
            tenant_var.reset(token)
        oidc, password_auth = self._oidc(tenant_id, rec)
        log.info("tenant %s loaded in %.1fs (%d types)", tenant_id, time.time() - t0,
                 len(services.typedefs.registry.defs), extra={"tenant": tenant_id})
        return Tenant(tenant_id, rec, services, oidc, password_auth, client, own)

    def _oidc(self, tenant_id: str, rec: dict):
        s = self.settings
        if not s.oidc_enabled:
            return None, None
        from .oidc import KeycloakPasswordAuthenticator, OidcAuthenticator
        realm = rec.get("realm") or tenant_id
        issuers = [i.format(tenant=realm, realm=realm) for i in _split(s.tenant_oidc_issuers)]
        jwks = s.tenant_oidc_jwks_url.format(tenant=realm, realm=realm) if s.tenant_oidc_jwks_url else None
        oidc = OidcAuthenticator(issuers, jwks, _split(s.oidc_clients), s.oidc_username_claim,
                                 _split(s.oidc_client_roles), s.oidc_leeway_secs)
        password_auth = None
        if s.oidc_password_login:
            token_url = oidc.jwks.url.replace("/protocol/openid-connect/certs", "/protocol/openid-connect/token")
            password_auth = KeycloakPasswordAuthenticator(oidc, token_url, s.oidc_password_client,
                                                          client_secret=s.oidc_password_client_secret)
        return oidc, password_auth

    async def _unload(self, tenant_id: str) -> None:
        t = self._tenants.pop(tenant_id, None)
        if t is None:
            return
        try:
            await t.services.stop()
        finally:
            if t.own_client:
                await t.client.close()
        log.info("tenant %s unloaded", tenant_id, extra={"tenant": tenant_id})

    async def unload(self, tenant_id: str) -> None:
        await self._unload(tenant_id)

    async def _evict_loop(self) -> None:
        idle = self.settings.tenant_idle_secs
        while True:
            await asyncio.sleep(max(5.0, min(60.0, idle / 4 if idle > 0 else 60.0)))
            if idle <= 0:
                continue
            now = time.monotonic()
            for tid, t in list(self._tenants.items()):
                if tid != self.default and t.in_flight == 0 and now - t.last_used > idle:
                    try:
                        await self._unload(tid)
                    except Exception:  # noqa: BLE001
                        log.exception("unloading tenant %s failed", tid)

    # ------------------------------------------------------------------ retention (all tenants)
    async def apply_retention(self) -> Dict[str, dict]:
        from .services import apply_retention
        from .store.es import EsStore
        out = {}
        for rec in await self.registry.list():
            if rec.get("status") != ACTIVE:
                continue
            tid = rec["id"]
            t = self._tenants.get(tid)
            settings = tenant_settings(self.settings, tid)
            if rec.get("retentionDays"):
                settings = settings.model_copy(update={"access_log_retention_days": rec["retentionDays"],
                                                       "clickstream_retention_days": rec["retentionDays"]})
            client, own = self.client, False
            if t is None and rec.get("esApiKey") and not self.settings.in_memory:
                from .store.es import make_client
                client = make_client(settings.model_copy(update={"es_api_key": rec["esApiKey"],
                                                                 "es_username": None}))
                own = True
            store = t.services.store if t is not None else EsStore(client, settings)
            try:
                out[tid] = await apply_retention(store, settings)
            except Exception as e:  # noqa: BLE001 - e.g. a tenant without indices yet
                log.debug("retention for tenant %s skipped: %s", tid, e)
            finally:
                if own:
                    await client.close()
        return out

    async def _retention_loop(self) -> None:
        while True:
            try:
                res = await self.apply_retention()
                if any(any(v.values()) for v in res.values()):
                    log.info("retention: deleted %s", res)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                log.exception("retention clean-up failed")
            await asyncio.sleep(6 * 3600)


class TenantMiddleware:
    """Resolves the tenant of a request (header from a trusted proxy, else the default tenant) and puts its
    context into ``request.state``: ``tenant``, ``services``.  Pure ASGI, so it runs before the session."""

    # answered without a tenant: health checks; the Kibana login's realm choice (it reads the tenant from its URL)
    OPEN_PATHS = ("/api/atlas/admin/liveness", "/api/atlas/admin/readiness", "/api/aurelius/kibana-discover")

    def __init__(self, app, manager: TenantManager, header: str, trusted_proxies: str):
        from .auth import _networks
        self.app = app
        self.manager = manager
        self.header = header.lower().encode("latin-1")
        self.proxies = _networks(trusted_proxies)

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)
        from .auth import _in_networks
        values = [v.decode("latin-1").strip() for k, v in scope.get("headers") or [] if k == self.header]
        peer = (scope.get("client") or ("", 0))[0]
        path = scope.get("path", "")
        tenant_id: Optional[str] = None
        if values:
            if not _in_networks(peer, self.proxies):
                return await _error(send, 400, "Tenant header not accepted from this client")
            if len(values) > 1 or len(set(values)) > 1:
                return await _error(send, 400, "More than one tenant header")
            tenant_id = values[0]
        elif not path.startswith(self.OPEN_PATHS):
            tenant_id = self.manager.default
        state = scope.setdefault("state", {})
        if tenant_id is None:
            if path.startswith(self.OPEN_PATHS):
                return await self.app(scope, receive, send)
            return await _error(send, 404, "No tenant in the request")
        try:
            tenant = await self.manager.get(tenant_id)
        except TenantError as e:
            return await _error(send, e.status, e.message)
        state["tenant"] = tenant
        state["services"] = tenant.services
        tenant.in_flight += 1
        from .logctx import tenant_var
        token = tenant_var.set(tenant.id)
        try:
            await self.app(scope, receive, send)
        finally:
            tenant_var.reset(token)
            tenant.in_flight -= 1
            tenant.last_used = time.monotonic()


async def _error(send, status: int, message: str) -> None:
    import json
    body = json.dumps({"errorCode": f"ATLAS-{status}-00-000", "errorMessage": message}).encode("utf-8")
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]})
    await send({"type": "http.response.body", "body": body})


class TenantSessions:
    """One session cookie per tenant (``ATLASSESSIONID_<tenant>``): a browser logged in to two tenants keeps two
    independent sessions, and a cookie of one tenant is never read by another."""

    def __init__(self, app, **session_kwargs):
        self.app = app
        self.kwargs = session_kwargs
        self._by_tenant: Dict[str, Any] = {}

    async def __call__(self, scope, receive, send):
        from starlette.middleware.sessions import SessionMiddleware
        tenant = (scope.get("state") or {}).get("tenant")
        key = tenant.id if tenant is not None else ""
        mw = self._by_tenant.get(key)
        if mw is None:
            cookie = f"ATLASSESSIONID_{key}" if key else "ATLASSESSIONID"
            mw = self._by_tenant[key] = SessionMiddleware(self.app, session_cookie=cookie, **self.kwargs)
        await mw(scope, receive, send)
