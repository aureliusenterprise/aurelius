"""OpenID Connect bearer tokens (Keycloak) as a second way to authenticate API calls.

The Aurelius frontend logs users in with Keycloak (keycloak-js) and sends the access token as
``Authorization: Bearer <jwt>``.  Apache Atlas accepted these through its Keycloak adapter
(``atlas.authentication.method.keycloak=true``, ``principal-attribute=preferred_username``,
``autodetect-bearer-only``); pyatlas validates them itself:

* the signature against the realm's JSON Web Key Set (fetched from ``PYATLAS_OIDC_JWKS_URL`` or the
  issuer's ``/protocol/openid-connect/certs``; cached, re-fetched when a token names an unknown key id),
* ``iss`` must be one of ``PYATLAS_OIDC_ISSUERS`` (the URL the *browser* uses, e.g.
  ``https://example.com/aurelius/auth/realms/m4i``; several are allowed for internal and external names),
* ``exp`` / ``nbf`` / ``iat`` with a small clock skew,
* optionally the client (``azp``) or audience (``aud``) against ``PYATLAS_OIDC_CLIENTS``; empty = any client of
  the realm, as the Atlas adapter did.

The user name is the ``preferred_username`` claim (``PYATLAS_OIDC_USERNAME_CLAIM``); the groups used by the
authorizer's ``groupRoles`` are the realm roles (``realm_access.roles``) plus, when ``PYATLAS_OIDC_CLIENT_ROLES``
names clients, their client roles.  Service accounts (client credentials grant) work the same way.
"""
from __future__ import annotations

import json
import logging
import threading
import time
import urllib.request
from typing import Dict, Iterable, List, Optional, Sequence, Set

log = logging.getLogger(__name__)

ALLOWED_ALGORITHMS = ("RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512")


class InvalidToken(Exception):
    pass


class JwksCache:
    """Keys by ``kid``; refreshed after ``ttl`` seconds or when an unknown key id shows up (at most every
    ``min_refresh`` seconds, so forged key ids cannot make pyatlas hammer Keycloak)."""

    def __init__(self, url: str, ttl: float = 3600, min_refresh: float = 30, timeout: float = 10,
                 fetch=None):
        self.url = url
        self.ttl = ttl
        self.min_refresh = min_refresh
        self.timeout = timeout
        self._fetch = fetch or self._http_fetch
        self._keys: Dict[str, object] = {}
        self._loaded = 0.0
        self._lock = threading.Lock()

    def _http_fetch(self) -> dict:
        req = urllib.request.Request(self.url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:  # noqa: S310 - configured URL
            return json.loads(r.read().decode("utf-8"))

    def _load(self) -> None:
        import jwt
        data = self._fetch()
        keys = {}
        for jwk in data.get("keys") or []:
            if jwk.get("use", "sig") != "sig":
                continue
            try:
                keys[jwk.get("kid") or ""] = jwt.PyJWK(jwk).key
            except Exception as e:  # noqa: BLE001 - unsupported key types are skipped
                log.debug("skipping JWK %s: %s", jwk.get("kid"), e)
        self._keys = keys
        self._loaded = time.time()

    def key(self, kid: Optional[str]):
        now = time.time()
        with self._lock:
            if not self._keys or now - self._loaded > self.ttl:
                self._safe_load()
            k = self._keys.get(kid or "")
            if k is None and now - self._loaded > self.min_refresh:
                self._safe_load()
                k = self._keys.get(kid or "")
        if k is None:
            raise InvalidToken("unknown signing key")
        return k

    def _safe_load(self) -> None:
        try:
            self._load()
        except Exception as e:  # noqa: BLE001
            log.warning("could not load the OIDC signing keys from %s: %s", self.url, e)
            if not self._keys:
                raise InvalidToken("signing keys not available") from None


class OidcAuthenticator:
    def __init__(self, issuers: Sequence[str], jwks_url: Optional[str] = None, clients: Iterable[str] = (),
                 username_claim: str = "preferred_username", client_roles: Iterable[str] = (),
                 leeway: int = 30, jwks: Optional[JwksCache] = None):
        self.issuers = [i.rstrip("/") for i in issuers if i]
        if not self.issuers:
            raise ValueError("PYATLAS_OIDC_ISSUERS is required when OIDC is enabled")
        self.jwks = jwks or JwksCache(jwks_url or f"{self.issuers[0]}/protocol/openid-connect/certs")
        self.clients: Set[str] = {c for c in clients if c}
        self.username_claim = username_claim
        self.client_roles = [c for c in client_roles if c]
        self.leeway = leeway

    def validate(self, token: str) -> dict:
        import jwt
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise InvalidToken("malformed token") from None
        alg = header.get("alg")
        if alg not in ALLOWED_ALGORITHMS:          # never "none" or HMAC with a public key
            raise InvalidToken(f"algorithm {alg} not accepted")
        key = self.jwks.key(header.get("kid"))
        try:
            claims = jwt.decode(token, key=key, algorithms=[alg], leeway=self.leeway,
                                options={"require": ["exp", "iss"], "verify_aud": False})
        except jwt.ExpiredSignatureError:
            raise InvalidToken("token expired") from None
        except jwt.PyJWTError as e:
            raise InvalidToken(f"invalid token: {e}") from None
        if str(claims.get("iss", "")).rstrip("/") not in self.issuers:
            raise InvalidToken("token issuer not accepted")
        if claims.get("typ") not in (None, "Bearer"):     # Keycloak ID / refresh tokens are not access tokens
            raise InvalidToken("not an access token")
        if self.clients:
            aud = claims.get("aud") or []
            aud = [aud] if isinstance(aud, str) else list(aud)
            if claims.get("azp") not in self.clients and not self.clients.intersection(aud):
                raise InvalidToken("token client not accepted")
        return claims

    def user_from_claims(self, claims: dict):
        from .auth import User
        name = claims.get(self.username_claim) or claims.get("sub")
        if not name:
            raise InvalidToken(f"token has no {self.username_claim}")
        return User(str(name), set(self.groups(claims)))

    def groups(self, claims: dict) -> List[str]:
        out = list((claims.get("realm_access") or {}).get("roles") or [])
        for client in self.client_roles:
            out += ((claims.get("resource_access") or {}).get(client) or {}).get("roles") or []
        return out

    def authenticate(self, token: str):
        return self.user_from_claims(self.validate(token))


def from_settings(settings) -> Optional[OidcAuthenticator]:
    if not settings.oidc_enabled:
        return None
    split = lambda s: [x.strip() for x in (s or "").split(",") if x.strip()]  # noqa: E731
    return OidcAuthenticator(split(settings.oidc_issuers), settings.oidc_jwks_url, split(settings.oidc_clients),
                             settings.oidc_username_claim, split(settings.oidc_client_roles),
                             settings.oidc_leeway_secs)
