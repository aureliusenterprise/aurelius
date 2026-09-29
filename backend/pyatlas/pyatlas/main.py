"""FastAPI application factory."""
from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .auth import AuthMiddleware, FileAuthenticator, LoginThrottle
from .aurelius import api as aurelius_api
from .oidc import from_settings as oidc_from_settings
from .oidc import password_authenticator_from_settings
from .config import Settings, get_settings
from .errors import AtlasBaseException
from .logctx import TenantFilter
from .logctx import configure as configure_logging
from .services import Services
from .store.es import make_client
from .web import admin_api, entity_api, glossary_api, other_api, types_api

log = logging.getLogger("pyatlas")
request_log = logging.getLogger("pyatlas.request")

# secrets that were shipped in earlier versions / examples and must never be used
KNOWN_DEFAULT_SECRETS = {"change-me-please-change-me-please", "please-change-this-secret-value"}


class BodySizeLimit:
    """Rejects request bodies larger than ``max_bytes`` (413) - declared or streamed."""

    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or self.max_bytes <= 0:
            return await self.app(scope, receive, send)
        for k, v in scope.get("headers") or []:
            if k == b"content-length":
                try:
                    if int(v) > self.max_bytes:
                        return await _too_large(send)
                except ValueError:
                    pass
        seen = 0

        async def limited_receive():
            nonlocal seen
            msg = await receive()
            if msg["type"] == "http.request":
                seen += len(msg.get("body", b""))
                if seen > self.max_bytes:
                    raise _BodyTooLarge()
            return msg
        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await _too_large(send)


class _BodyTooLarge(Exception):
    pass


async def _too_large(send):
    body = b'{"errorCode":"ATLAS-413-00-001","errorMessage":"Request body too large"}'
    await send({"type": "http.response.start", "status": 413,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]})
    await send({"type": "http.response.body", "body": body})


# Atlas' HeadersUtil defaults
SECURITY_HEADERS = [
    (b"x-frame-options", b"DENY"),
    (b"x-content-type-options", b"nosniff"),
    (b"x-xss-protection", b"1; mode=block"),
    (b"content-security-policy", b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:; "
                                 b"connect-src 'self'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline';"
                                 b"font-src 'self' data:"),
    (b"referrer-policy", b"same-origin"),
]


class SecurityHeaders:
    def __init__(self, app, hsts: bool = False):
        self.app = app
        self.headers = list(SECURITY_HEADERS)
        if hsts:
            self.headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_headers(msg):
            if msg["type"] == "http.response.start":
                present = {k.lower() for k, _ in msg.get("headers") or []}
                msg = dict(msg)
                msg["headers"] = list(msg.get("headers") or []) + [h for h in self.headers if h[0] not in present]
            await send(msg)
        await self.app(scope, receive, send_with_headers)


class StripTrailingSlash:
    """Atlas (Jersey) accepts ``/api/atlas/v2/types/typedefs/``; so do we (the official Python client uses it)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/") and len(path) > 5 and path.endswith("/"):
                scope = dict(scope)
                scope["path"] = path.rstrip("/")
                if scope.get("raw_path"):
                    scope["raw_path"] = scope["raw_path"].rstrip(b"/")
        await self.app(scope, receive, send)


def create_app(settings: Optional[Settings] = None, es_client=None) -> FastAPI:
    settings = settings or get_settings()
    client = es_client or make_client(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if app.state.tenants is not None:
            await app.state.tenants.start()
            log.info("pyatlas started for several tenants (loaded: %s)", ", ".join(app.state.tenants.loaded) or "-")
        else:
            await app.state.services.start()
            log.info("pyatlas started: %d types loaded", len(app.state.services.typedefs.registry.defs))
        yield
        if app.state.tenants is not None:
            await app.state.tenants.stop()
        else:
            await app.state.services.stop()
        if es_client is None:
            await client.close()

    app = FastAPI(title="pyatlas", version=settings.version, lifespan=lifespan,
                  description="Apache Atlas compatible metadata server backed by Elasticsearch",
                  docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)
    app.state.settings = settings
    app.state.es = client
    app.state.tenants = None
    if settings.tenancy_enabled:
        from .tenancy import TenantManager
        app.state.tenants = TenantManager(client, settings)
        app.state.services = None           # every request gets the services of its tenant (request.state)
    else:
        app.state.services = Services(client, settings)

    @app.exception_handler(AtlasBaseException)
    async def atlas_error(request: Request, exc: AtlasBaseException):
        return JSONResponse(exc.to_json(), status_code=exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse({"errorCode": "ATLAS-400-00-029", "errorMessage": str(exc.errors())}, status_code=400)

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        # details go to the server log only; the client gets an id to find them
        import uuid as _uuid
        err_id = _uuid.uuid4().hex[:12]
        log.exception("unhandled error %s on %s %s", err_id, request.method, request.url.path)
        return JSONResponse({"errorCode": "ATLAS-500-00-001", "errorMessage": f"Internal server error (id {err_id})"},
                            status_code=500)

    # one line per API call with tenant, user, status and duration (Kibana "Aurelius health"); DEBUG in text mode,
    # where uvicorn's access log already shows the requests
    request_log_level = logging.INFO if (settings.log_format or "").lower() == "json" else logging.DEBUG

    @app.middleware("http")
    async def request_timing(request: Request, call_next):
        import time as _t
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)
        services = getattr(request.state, "services", None) or app.state.services
        if services is None:
            return await call_next(request)
        sid = None
        if path.startswith("/api/atlas/v2/search/"):
            user = getattr(getattr(request.state, "user", None), "name", None) or "anonymous"
            sid = services.active_searches.register(user)
        t0 = _t.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            if sid:
                services.active_searches.unregister(sid)
            route = request.scope.get("route")
            name = getattr(route, "name", None) or path
            ms = (_t.perf_counter() - t0) * 1000
            services.request_metrics.record(name, ms)
            request_log.log(request_log_level, "%s %s %s %.0fms", request.method, path, status, ms,
                             extra={"method": request.method, "path": path, "status": status,
                                    "duration_ms": round(ms, 1),
                                    "user": getattr(getattr(request.state, "user", None), "name", None)})

    _write_paths = ("/api/atlas/v2/entity", "/api/atlas/v2/relationship", "/api/atlas/entities", "/api/lin_api/")

    @app.middleware("http")
    async def aurelius_read_your_writes(request: Request, call_next):
        # the frontend opens the details page right after saving: bring the Aurelius documents up to date
        # before answering an entity/relationship change (bounded; the debounced rebuild catches up otherwise)
        response = await call_next(request)
        services = getattr(request.state, "services", None) or app.state.services
        a = services.aurelius if services is not None else None
        timeout = settings.aurelius_sync_write_timeout_secs
        if a is not None and timeout > 0 and request.method in ("POST", "PUT", "DELETE") \
                and request.url.path.startswith(_write_paths) and response.status_code < 400:
            import asyncio as _asyncio
            try:
                await _asyncio.wait_for(_asyncio.shield(a.settle()), timeout)
            except _asyncio.TimeoutError:
                log.info("Aurelius documents still rebuilding after %ss; answering %s", timeout, request.url.path)
            except Exception:  # noqa: BLE001 - the debounced rebuild retries
                log.exception("Aurelius rebuild after %s failed", request.url.path)
        return response

    @app.middleware("http")
    async def typedef_freshness(request: Request, call_next):
        # pick up typedef changes made through other pyatlas nodes (checked at most every few seconds)
        services = getattr(request.state, "services", None) or app.state.services
        if services is not None and request.url.path.startswith("/api/"):
            try:
                await services.typedefs.ensure_fresh()
            except Exception:  # pragma: no cover - never fail a request because of this check
                log.debug("typedef freshness check failed", exc_info=True)
        return await call_next(request)

    for r in (types_api.router, entity_api.router, other_api.relationship_router, other_api.search_router,
              other_api.lineage_router, glossary_api.router, admin_api.router, admin_api.recovery_router,
              aurelius_api.router, aurelius_api.lineage_router):
        app.include_router(r)

    file_users = settings.file_users_enabled and not settings.tenancy_enabled
    authenticators = [FileAuthenticator(settings.users_file)] if file_users else []
    if settings.tenancy_enabled:
        log.info("multi-tenant: users log in through the Keycloak realm of their tenant (users file not used)")
    elif not settings.file_users_enabled:
        log.info("users file disabled (PYATLAS_FILE_USERS_ENABLED=false): only Keycloak users can log in")
    oidc = oidc_from_settings(settings) if not settings.tenancy_enabled else None
    keycloak_login = password_authenticator_from_settings(settings, oidc)
    if keycloak_login is not None:
        authenticators.append(keycloak_login)
    if not settings.auth_enabled:
        log.warning("SECURITY: authentication is DISABLED (PYATLAS_AUTH_ENABLED=false) - everybody is admin")
    app.add_middleware(AuthMiddleware, authenticators=authenticators, enabled=settings.auth_enabled,
                       csrf_enabled=settings.csrf_enabled, csrf_browser_useragents=settings.csrf_browser_useragents,
                       throttle=LoginThrottle(settings.login_max_failures, settings.login_lockout_secs),
                       oidc=oidc, trusted_proxies=settings.trusted_proxies)
    secret = settings.session_secret
    if not secret or secret in KNOWN_DEFAULT_SECRETS or len(secret) < 16:
        if secret:
            log.warning("SECURITY: PYATLAS_SESSION_SECRET is a published default or too short - ignoring it")
        log.warning("PYATLAS_SESSION_SECRET is not set: using a random key (UI sessions end on restart and do not "
                    "work across several pyatlas nodes)")
        secret = secrets.token_urlsafe(48)
    session_kwargs = dict(secret_key=secret, same_site="lax", https_only=settings.session_cookie_secure,
                          max_age=settings.session_max_age_secs if settings.session_max_age_secs > 0 else None)
    if settings.tenancy_enabled:
        from .tenancy import TenantMiddleware, TenantSessions
        app.add_middleware(TenantSessions, **session_kwargs)
        # outside the sessions: the tenant decides which session cookie is read
        app.add_middleware(TenantMiddleware, manager=app.state.tenants, header=settings.tenant_header,
                           trusted_proxies=settings.trusted_proxies)
    else:
        app.add_middleware(SessionMiddleware, session_cookie="ATLASSESSIONID", **session_kwargs)
    if settings.security_headers:
        app.add_middleware(SecurityHeaders, hsts=settings.hsts)
    app.add_middleware(BodySizeLimit, max_bytes=settings.max_upload_mb * 1024 * 1024)
    app.add_middleware(StripTrailingSlash)

    ui_dir = settings.ui_dir
    if ui_dir.exists():
        @app.get("/login.jsp", include_in_schema=False)
        async def login_page():
            return FileResponse(ui_dir / "login.jsp", media_type="text/html")

        @app.get("/", include_in_schema=False)
        async def root():
            return RedirectResponse("index.html")

        app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")
    return app


def app_factory() -> FastAPI:  # for `uvicorn pyatlas.main:app_factory --factory`
    settings = get_settings()
    if not any(isinstance(f, TenantFilter) for h in logging.getLogger().handlers for f in h.filters):
        configure_logging(settings.log_format)
    if settings.in_memory:
        from .store.memory import FakeElasticsearch
        log.warning("running with the IN-MEMORY store: data is lost on restart (demo/development only)")
        return create_app(settings, es_client=FakeElasticsearch())
    return create_app(settings)
