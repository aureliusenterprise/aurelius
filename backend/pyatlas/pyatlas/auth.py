"""Authentication, sessions and CSRF protection.

Atlas' file based authentication (``users-credentials.properties``, ``user=GROUP1,GROUP2::hash``) is used
via HTTP Basic auth for API clients and a session cookie for the web UI (``/j_spring_security_check`` login
form, like Atlas).  Password hashes are verified like Atlas' ``UserDao``: BCrypt (``$2a$``/``$2b$``/``$2y$``,
recommended - see ``scripts/hash_password.py``), SHA-256 salted with the user name (``sha256(pw + "{user}")``)
and, for old files, plain SHA-256.

Sessions are signed cookies (Starlette ``SessionMiddleware``).  They expire after
``PYATLAS_SESSION_MAX_AGE_SECS`` and every request re-checks that the user still exists; the groups are
taken from the current users file, not from the cookie.

CSRF protection is a port of Atlas' ``AtlasCSRFPreventionFilter``: API requests from browsers (by
User-Agent) that change data must carry the ``X-XSRF-HEADER`` header with the per-session token that
``GET /api/atlas/admin/session`` returns (both bundled UIs do this automatically).

The :class:`Authenticator` interface is where LDAP / Kerberos / OpenID Connect providers plug in later.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import logging
import re
import secrets
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from .authz import set_current_user

log = logging.getLogger(__name__)

CSRF_SESSION_KEY = "csrf"


class User:
    def __init__(self, name: str, groups: Set[str], source: str = "file"):
        self.name = name
        self.groups = groups
        # "file" = users file (its per-user roles apply), "oidc" = Keycloak (only the token's roles count)
        self.source = source


class Authenticator:
    def authenticate(self, username: str, password: str) -> Optional[User]:  # pragma: no cover - interface
        raise NotImplementedError

    def lookup(self, username: str) -> Optional[User]:  # pragma: no cover - interface
        """The user (with current groups) if it still exists; used to re-validate sessions."""
        raise NotImplementedError


def verify_password(password: str, stored: str, username: str) -> bool:
    """Atlas ``UserDao.checkEncrypted``: BCrypt, then SHA-256 salted with the user name, then plain SHA-256."""
    if not stored:
        return False
    if stored.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
        except (ImportError, ValueError):
            return False
    stored = stored.lower()
    salted = hashlib.sha256(f"{password}{{{username}}}".encode("utf-8")).hexdigest()
    if hmac.compare_digest(salted, stored):
        return True
    plain = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(plain, stored)


def hash_password(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


class FileAuthenticator(Authenticator):
    """Atlas-compatible ``users-credentials.properties`` (reloaded when the file changes)."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.users: Dict[str, Tuple[Set[str], str]] = {}
        self._mtime: Optional[float] = None
        self._lock = threading.Lock()
        self.reload()

    def reload(self) -> None:
        users: Dict[str, Tuple[Set[str], str]] = {}
        if not self.path.exists():
            log.warning("users file %s not found; nobody can log in", self.path)
        else:
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                user, rest = line.split("=", 1)
                if "::" not in rest:
                    continue
                groups, pwhash = rest.split("::", 1)
                users[user.strip()] = ({g.strip() for g in groups.split(",") if g.strip()}, pwhash.strip())
            self._mtime = self.path.stat().st_mtime
        self.users = users
        weak = [u for u, (_, h) in users.items() if not h.startswith("$2")]
        if weak:
            log.warning("users file: %s use SHA-256 password hashes; BCrypt is recommended "
                        "(python scripts/hash_password.py)", ", ".join(sorted(weak)))
        admin = users.get("admin")
        if admin and verify_password("admin", admin[1], "admin"):
            log.warning("SECURITY: user 'admin' still has the default password 'admin' - change it in %s", self.path)

    def _refresh(self) -> None:
        try:
            m = self.path.stat().st_mtime if self.path.exists() else None
        except OSError:
            return
        if m != self._mtime:
            with self._lock:
                self.reload()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        self._refresh()
        entry = self.users.get(username)
        if entry is None:
            # same amount of work as for an existing user (no user enumeration by timing)
            verify_password(password, "0" * 64, username)
            return None
        groups, pwhash = entry
        if verify_password(password, pwhash, username):
            return User(username, set(groups))
        return None

    def lookup(self, username: str) -> Optional[User]:
        self._refresh()
        entry = self.users.get(username)
        return User(username, set(entry[0])) if entry else None


class LoginThrottle:
    """Locks a user name for a client address for ``lockout_secs`` after ``max_failures`` failed logins within
    that period (keyed by name *and* address, so nobody can lock others out from elsewhere)."""

    def __init__(self, max_failures: int = 5, lockout_secs: int = 300):
        self.max_failures = max_failures
        self.lockout_secs = lockout_secs
        self.failures: Dict[str, List[float]] = {}

    def locked(self, username: str) -> bool:
        if self.max_failures <= 0:
            return False
        now = time.time()
        recent = [t for t in self.failures.get(username, []) if now - t < self.lockout_secs]
        self.failures[username] = recent
        return len(recent) >= self.max_failures

    def failed(self, username: str) -> None:
        self.failures.setdefault(username, []).append(time.time())
        if len(self.failures) > 100000:          # bound memory
            self.failures.clear()

    def succeeded(self, username: str) -> None:
        self.failures.pop(username, None)


PUBLIC_PREFIXES = ("/login.jsp", "/login.html", "/j_spring_security_check", "/css/", "/img/", "/js/",
                   "/ieerror.html", "/api/atlas/admin/liveness", "/api/atlas/admin/readiness", "/favicon.ico")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, authenticators: List[Authenticator], enabled: bool = True, csrf_enabled: bool = True,
                 csrf_header: str = "X-XSRF-HEADER", csrf_methods_to_ignore: str = "GET,OPTIONS,HEAD,TRACE",
                 csrf_browser_useragents: str = "^Mozilla.*,^Opera.*,^Chrome.*",
                 throttle: Optional[LoginThrottle] = None, oidc=None, trusted_proxies: str = ""):
        super().__init__(app)
        self.oidc = oidc
        self.trusted_proxies = _networks(trusted_proxies)
        self.authenticators = authenticators
        self.enabled = enabled
        self.csrf_enabled = csrf_enabled
        self.csrf_header = csrf_header
        self.csrf_ignore = {m.strip().upper() for m in csrf_methods_to_ignore.split(",") if m.strip()}
        self.browser_agents = [re.compile(p.strip()) for p in csrf_browser_useragents.split(",") if p.strip()]
        self.throttle = throttle or LoginThrottle()

    # ------------------------------------------------------------------ helpers
    def _basic(self, request: Request) -> Tuple[Optional[User], Optional[str]]:
        header = request.headers.get("authorization", "")
        if not header.lower().startswith("basic "):
            return None, None
        try:
            raw = base64.b64decode(header[6:].strip()).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return None, None
        if ":" not in raw:
            return None, None
        u, p = raw.split(":", 1)
        return self.check(u, p, self.client_ip(request)), u

    def client_ip(self, request: Request) -> str:
        """The client's address; behind a trusted proxy the last X-Forwarded-For entry (the address the proxy
        saw - earlier entries are sent by the client and cannot be trusted)."""
        peer = _client(request)
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd and _in_networks(peer, self.trusted_proxies):
            return fwd.split(",")[-1].strip() or peer
        return peer

    def check(self, username: str, password: str, client: str = "") -> Optional[User]:
        key = f"{username}|{client}"
        if self.throttle.locked(key):
            return None
        for a in self.authenticators:
            user = a.authenticate(username, password)
            if user is not None:
                self.throttle.succeeded(key)
                return user
        self.throttle.failed(key)
        return None

    def _lookup(self, username: str, source: Optional[str] = None) -> Optional[User]:
        for a in self.authenticators:
            if source is not None and getattr(a, "source", "file") != source:
                continue
            try:
                u = a.lookup(username)
            except NotImplementedError:  # pragma: no cover
                continue
            if u is not None:
                return u
        return None

    def _is_browser(self, request: Request) -> bool:
        ua = request.headers.get("user-agent")
        return bool(ua) and any(p.fullmatch(ua) for p in self.browser_agents)

    def _csrf_ok(self, request: Request) -> bool:
        if not self.csrf_enabled or request.method.upper() in self.csrf_ignore or not self._is_browser(request):
            return True
        sess = request.session if "session" in request.scope else {}
        token = sess.get(CSRF_SESSION_KEY)
        sent = request.headers.get(self.csrf_header)
        return bool(token) and sent is not None and hmac.compare_digest(sent, token)

    # ------------------------------------------------------------------ dispatch
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not self.enabled:
            request.state.user = User("admin", {"ADMIN"})
            set_current_user(request.state.user)
            return await call_next(request)
        header = request.headers.get("authorization", "")
        if header[:7].lower() == "bearer ":
            return await self._dispatch_bearer(request, call_next, header[7:].strip())
        sess = request.session if "session" in request.scope else {}
        user = None
        if sess.get("user"):
            # user removed from the users file -> session is dead; a Keycloak login is looked up in Keycloak's cache
            user = self._lookup(sess["user"], sess.get("src", "file"))
            if user is None:
                sess.clear()
        if user is None:
            import asyncio
            # password checks may call Keycloak (blocking HTTP): never on the event loop
            user, basic_name = await asyncio.to_thread(self._basic, request)
            if user is not None and _access_log(request) is not None:
                await _access_log(request).record(user.name, "basic", ip=self.client_ip(request), groups=user.groups)
            if user is None and basic_name is not None and path.startswith("/api/"):
                msg = "Too many failed logins, try again later" \
                    if self.throttle.locked(f"{basic_name}|{self.client_ip(request)}") \
                    else "Authentication required"
                return JSONResponse({"errorCode": "ATLAS-401-00-001", "errorMessage": msg}, status_code=401,
                                    headers={"WWW-Authenticate": 'Basic realm="atlas"'})
        if path == "/j_spring_security_check" and request.method == "POST":
            form = await request.form()
            name = str(form.get("j_username", ""))
            if self.throttle.locked(f"{name}|{self.client_ip(request)}"):
                return JSONResponse({"msgDesc": "Too many failed logins, try again later"}, status_code=401)
            import asyncio
            user = await asyncio.to_thread(self.check, name, str(form.get("j_password", "")), self.client_ip(request))
            if user is None:
                return JSONResponse({"msgDesc": "Invalid User credentials"}, status_code=401)
            sess.clear()                             # no session fixation: a fresh session per login
            request.session["user"] = user.name
            request.session["src"] = user.source
            request.session["login"] = int(time.time())
            request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)
            if _access_log(request) is not None:
                await _access_log(request).record(user.name, "form", ip=self.client_ip(request), groups=user.groups)
            return JSONResponse({"msgDesc": "Login Successful"})
        if path == "/logout.html":
            if "session" in request.scope:
                request.session.clear()
            return RedirectResponse("login.jsp", status_code=302)
        if user is None:
            if path.startswith(PUBLIC_PREFIXES):
                request.state.user = None
                return await call_next(request)
            if path.startswith("/api/"):
                return JSONResponse({"errorCode": "ATLAS-401-00-001", "errorMessage": "Authentication required"},
                                    status_code=401, headers={"WWW-Authenticate": 'Basic realm="atlas"'})
            return RedirectResponse("login.jsp", status_code=302)
        if path.startswith("/api/") and not self._csrf_ok(request):
            return JSONResponse({"msgDesc": "Missing header or invalid Header value for CSRF Vulnerability Protection"},
                                status_code=400)
        request.state.user = user
        set_current_user(user)
        response: Response = await call_next(request)
        return response


    async def _dispatch_bearer(self, request: Request, call_next, token: str):
        """OIDC access token (Keycloak): no session, no CSRF check (browsers never attach it on their own)."""
        import asyncio
        from .oidc import InvalidToken
        if self.oidc is None:
            return _bearer_error("Bearer tokens are not accepted (OIDC is not configured)")
        try:
            claims = await asyncio.to_thread(self.oidc.validate, token)
            user = self.oidc.user_from_claims(claims)
        except InvalidToken as e:
            return _bearer_error(str(e))
        access = _access_log(request)
        if access is not None:
            await access.record(user.name, "keycloak", access.key_for_token(claims, user.name),
                                client=claims.get("azp"), ip=self.client_ip(request), groups=user.groups)
        request.state.user = user
        request.state.auth_method = "oidc"
        set_current_user(user)
        return await call_next(request)


def _bearer_error(message: str) -> JSONResponse:
    return JSONResponse({"errorCode": "ATLAS-401-00-001", "errorMessage": f"Authentication failed: {message}"},
                        status_code=401, headers={"WWW-Authenticate": 'Bearer realm="atlas", error="invalid_token"'})


def _networks(spec: str):
    import ipaddress
    out = []
    for part in (spec or "").split(","):
        part = part.strip()
        if part:
            try:
                out.append(ipaddress.ip_network(part, strict=False))
            except ValueError:
                log.warning("ignoring invalid trusted proxy %r", part)
    return out


def _in_networks(address: str, networks) -> bool:
    import ipaddress
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    return any(ip in n for n in networks)


def _access_log(request: Request):
    services = getattr(request.app.state, "services", None)
    return getattr(services, "access_log", None)


def _client(request: Request) -> str:
    return request.client.host if request.client else ""


def csrf_token(request: Request) -> str:
    """The session's CSRF token (created when missing); returned by ``GET /admin/session``."""
    if "session" not in request.scope:
        return ""
    tok = request.session.get(CSRF_SESSION_KEY)
    if not tok and request.session.get("user"):
        tok = request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)
    return tok or ""
