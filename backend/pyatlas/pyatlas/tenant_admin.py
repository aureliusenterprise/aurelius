"""``aurelius-admin``: sets up the platform and creates, changes and removes tenants.

    python -m pyatlas.tenant_admin platform init
    python -m pyatlas.tenant_admin tenant create acme --name "ACME" [--admin-user anna --admin-email a@acme.com]
                                                      [--sample-data] [--migrate-from atlas] [--retention-days 180]
    python -m pyatlas.tenant_admin tenant list | show acme | suspend acme | resume acme
    python -m pyatlas.tenant_admin tenant entra acme --directory-id <id> --client-id <id> --client-secret <secret>
    python -m pyatlas.tenant_admin tenant export acme --out acme.zip
    python -m pyatlas.tenant_admin tenant delete acme --yes

(in the compose stack: ``docker compose run --rm aurelius-admin tenant create acme``).  Every command is idempotent:
``tenant create`` for an existing tenant brings it up to date (clients, keys, space, dashboards) and keeps its data.

A tenant consists of

1. its record in the tenant registry (``aurelius_platform_tenants``),
2. its Keycloak realm (id and name = tenant id): roles ``ROLE_ADMIN``, ``DATA_STEWARD``, ``DATA_SCIENTIST``; the
   frontend client ``m4i_atlas`` (redirects to ``/<ns>/<tenant>/atlas/*``); the proxy's confidential client
   ``aurelius_proxy`` for the Kibana login; login events on; brute force protection and password policy,
3. its indices ``aurelius_<tenant>_*`` (created by pyatlas on first use) and two Elasticsearch API keys: pyatlas'
   (all privileges on ``aurelius_<tenant>_*``, nothing else) and Kibana's (read on those indices and on the log data
   streams ``logs-aurelius.*-<tenant>``, all features in Kibana space ``<tenant>``),
4. its Kibana space with the data views and the dashboards "Aurelius activity", "usage" and "health",
5. the proxy's files in ``TENANTS_DIR``: the realm as OpenID Connect provider of the Kibana login
   (``oidc/<issuer>.provider|.client|.conf``) and the tenant's Kibana key (``kibana-keys.txt``),
6. an index template that gives its log data streams the tenant's retention.

``platform init`` creates what all tenants share: the registry, Elasticsearch users for Kibana, pyatlas and the log
shipper, the log routing pipeline, the operators' realm ``platform`` and Kibana space ``platform``.

Settings (environment): AURELIUS_PUBLIC_URL, AURELIUS_NS, KEYCLOAK_URL (inside the network, with its path),
KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, KEYCLOAK_THEME, ES_URL, ES_USERNAME, ES_PASSWORD, KIBANA_URL (inside the
network, with the base path), TENANTS_DIR, KIBANA_SYSTEM_PASSWORD, PYATLAS_ES_PASSWORD, FILEBEAT_PASSWORD,
AURELIUS_OPERATOR_PASSWORD, LOG_RETENTION_DAYS; ``--dry-run`` prints the plan without changing anything.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .tenancy import ACTIVE, REGISTRY_MAPPING, check_tenant_id

log = logging.getLogger("aurelius-admin")

ROLES = {"ROLE_ADMIN": "Aurelius administrator (also Kibana)", "DATA_STEWARD": "Maintains the data governance model",
         "DATA_SCIENTIST": "Reads the data governance model"}
FRONTEND_CLIENT = "m4i_atlas"
PROXY_CLIENT = "aurelius_proxy"
LOGS_PIPELINE = "aurelius-logs"
ENRICH_TENANTS = "aurelius-tenants"
ENRICH_REALMS = "aurelius-realms"
LOG_SOURCES = ("pyatlas", "proxy", "keycloak")
SECRET_FIELDS = ("esApiKey", "kibanaApiKey", "proxyClientSecret")


class AdminError(Exception):
    pass


# --------------------------------------------------------------------------------------------------- configuration
@dataclass
class Config:
    public_url: str = "http://localhost:9090"
    ns: str = "aurelius"
    keycloak_url: str = "http://keycloak:8080/aurelius/auth"
    keycloak_admin: str = "admin"
    keycloak_admin_password: str = ""
    keycloak_theme: str = "m4i"
    es_url: str = "http://elasticsearch:9200"
    es_username: str = "elastic"
    es_password: str = ""
    kibana_url: str = "http://kibana:5601/aurelius/kibana"
    tenants_dir: Path = Path("/tenants")
    kibana_system_password: str = ""
    pyatlas_es_password: str = ""
    filebeat_password: str = ""
    operator_password: str = ""
    log_retention_days: int = 180
    platform_prefix: str = "aurelius_platform"
    platform_realm: str = "platform"
    dry_run: bool = False
    skip: Tuple[str, ...] = ()           # parts to leave out: keycloak, elasticsearch, kibana, proxy

    @classmethod
    def from_env(cls, **overrides) -> "Config":
        e = os.environ.get
        c = cls(public_url=e("AURELIUS_PUBLIC_URL", cls.public_url).rstrip("/"), ns=e("AURELIUS_NS", cls.ns),
                keycloak_url=e("KEYCLOAK_URL", cls.keycloak_url).rstrip("/"),
                keycloak_admin=e("KEYCLOAK_ADMIN", cls.keycloak_admin),
                keycloak_admin_password=e("KEYCLOAK_ADMIN_PASSWORD", ""),
                keycloak_theme=e("KEYCLOAK_THEME", cls.keycloak_theme),
                es_url=e("ES_URL", cls.es_url).rstrip("/"), es_username=e("ES_USERNAME", cls.es_username),
                es_password=e("ES_PASSWORD", ""), kibana_url=e("KIBANA_URL", cls.kibana_url).rstrip("/"),
                tenants_dir=Path(e("TENANTS_DIR", str(cls.tenants_dir))),
                kibana_system_password=e("KIBANA_SYSTEM_PASSWORD", ""),
                pyatlas_es_password=e("PYATLAS_ES_PASSWORD", ""), filebeat_password=e("FILEBEAT_PASSWORD", ""),
                operator_password=e("AURELIUS_OPERATOR_PASSWORD", ""),
                log_retention_days=int(e("LOG_RETENTION_DAYS", str(cls.log_retention_days))),
                platform_prefix=e("PYATLAS_TENANT_PLATFORM_PREFIX", cls.platform_prefix),
                platform_realm=e("PYATLAS_TENANT_PLATFORM_REALM", cls.platform_realm))
        for k, v in overrides.items():
            setattr(c, k, v)
        return c

    def issuer(self, realm: str) -> str:
        return f"{self.public_url}/{self.ns}/auth/realms/{realm}"

    @property
    def registry_index(self) -> str:
        return f"{self.platform_prefix}_tenants"

    @property
    def settings_index(self) -> str:
        return f"{self.platform_prefix}_settings"


# --------------------------------------------------------------------------------------------------- HTTP
Transport = Callable[[str, str, Dict[str, str], Optional[bytes]], Tuple[int, bytes]]


def urllib_transport(method: str, url: str, headers: Dict[str, str], body: Optional[bytes]) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 - configured URLs
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


class Http:
    def __init__(self, base: str, transport: Transport, auth: Callable[[], Dict[str, str]] = lambda: {},
                 dry_run: bool = False, name: str = ""):
        self.base = base.rstrip("/")
        self.transport = transport
        self.auth = auth
        self.dry_run = dry_run
        self.name = name

    def call(self, method: str, path: str, body: Any = None, ok=(200, 201, 204), headers=None, form=None,
             raw: Optional[bytes] = None, content_type: str = "application/json") -> Tuple[int, Any]:
        url = self.base + path
        h = {"Accept": "application/json", **self.auth(), **(headers or {})}
        data = None
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            h["Content-Type"] = "application/x-www-form-urlencoded"
        elif raw is not None:
            data, h["Content-Type"] = raw, content_type
        elif body is not None:
            data, h["Content-Type"] = json.dumps(body).encode(), "application/json"
        if self.dry_run and method != "GET":
            log.info("[dry-run] %s %s %s", method, self.name, path)
            return 200, {}
        status, content = self.transport(method, url, h, data)
        try:
            parsed = json.loads(content) if content else None
        except ValueError:
            parsed = content.decode("utf-8", "replace")
        if ok is not None and status not in ok:
            raise AdminError(f"{self.name} {method} {path}: HTTP {status}: {str(parsed)[:500]}")
        return status, parsed


# --------------------------------------------------------------------------------------------------- Keycloak
def realm_representation(tenant: str, display_name: str, cfg: Config, proxy_secret: str) -> dict:
    """A tenant's realm: the same template for every tenant (id = realm name = tenant id)."""
    rep = {
        "id": tenant, "realm": tenant, "enabled": True, "displayName": display_name,
        "sslRequired": "external", "registrationAllowed": False, "loginWithEmailAllowed": True,
        "resetPasswordAllowed": True, "accessTokenLifespan": 900, "ssoSessionIdleTimeout": 1800,
        "ssoSessionMaxLifespan": 36000, "bruteForceProtected": True, "failureFactor": 10,
        "waitIncrementSeconds": 60, "maxFailureWaitSeconds": 900,
        "passwordPolicy": "length(8) and notUsername",
        # login events: kept 90 days in Keycloak, logged for the tenant's Kibana (jboss-logging listener)
        "eventsEnabled": True, "eventsExpiration": 90 * 86400, "eventsListeners": ["jboss-logging"],
        "adminEventsEnabled": True, "adminEventsDetailsEnabled": False,
        "roles": {"realm": [{"name": n, "description": d} for n, d in ROLES.items()]},
        "clients": [frontend_client(tenant, cfg), proxy_client(cfg, proxy_secret)],
    }
    if cfg.keycloak_theme:
        rep.update(loginTheme=cfg.keycloak_theme, accountTheme=cfg.keycloak_theme, emailTheme=cfg.keycloak_theme)
    return rep


def frontend_client(tenant: str, cfg: Config, legacy: bool = False) -> dict:
    base = f"{cfg.public_url}/{cfg.ns}/{tenant}/atlas/"
    redirects = [f"{base}*"] + ([f"{cfg.public_url}/{cfg.ns}/atlas/*"] if legacy else [])
    return {"clientId": FRONTEND_CLIENT, "name": "Aurelius Atlas", "enabled": True, "publicClient": True,
            "protocol": "openid-connect", "standardFlowEnabled": True, "implicitFlowEnabled": False,
            # the Atlas UIs (/<ns>/<tenant>/atlas2/) check user name + password with Keycloak
            "directAccessGrantsEnabled": True, "rootUrl": base, "redirectUris": redirects, "webOrigins": ["+"],
            "attributes": {"post.logout.redirect.uris": "+"},
            "fullScopeAllowed": True, "defaultClientScopes": ["web-origins", "roles", "profile", "email"],
            "optionalClientScopes": ["offline_access"]}


def proxy_client(cfg: Config, secret: str) -> dict:
    return {"clientId": PROXY_CLIENT, "name": "Aurelius reverse proxy (Kibana login)", "enabled": True,
            "protocol": "openid-connect", "publicClient": False, "secret": secret, "standardFlowEnabled": True,
            "directAccessGrantsEnabled": False, "serviceAccountsEnabled": False,
            "redirectUris": [f"{cfg.public_url}/{cfg.ns}/kibana-oidc/callback"], "webOrigins": ["+"],
            "attributes": {"post.logout.redirect.uris": f"{cfg.public_url}/{cfg.ns}/*"},
            "protocolMappers": [{"name": "realm roles as roles", "protocol": "openid-connect",
                                 "protocolMapper": "oidc-usermodel-realm-role-mapper", "consentRequired": False,
                                 "config": {"multivalued": "true", "claim.name": "roles", "jsonType.label": "String",
                                            "id.token.claim": "true", "access.token.claim": "true",
                                            "userinfo.token.claim": "true"}}]}


class Keycloak:
    def __init__(self, cfg: Config, transport: Transport):
        self.cfg = cfg
        self._token: Optional[str] = None
        self._expires = 0.0
        self.http = Http(cfg.keycloak_url, transport, self._auth, cfg.dry_run, "keycloak")
        self.raw = Http(cfg.keycloak_url, transport, name="keycloak")

    def _auth(self) -> Dict[str, str]:
        if not self._token or time.time() > self._expires:
            _, r = self.raw.call("POST", "/realms/master/protocol/openid-connect/token", form={
                "grant_type": "password", "client_id": "admin-cli", "username": self.cfg.keycloak_admin,
                "password": self.cfg.keycloak_admin_password})
            self._token = r["access_token"]
            self._expires = time.time() + max(10, int(r.get("expires_in", 60)) - 15)
        return {"Authorization": f"Bearer {self._token}"}

    def realm(self, realm: str) -> Optional[dict]:
        status, r = self.http.call("GET", f"/admin/realms/{realm}", ok=(200, 404))
        return r if status == 200 else None

    def client(self, realm: str, client_id: str) -> Optional[dict]:
        _, r = self.http.call("GET", f"/admin/realms/{realm}/clients?clientId={urllib.parse.quote(client_id)}")
        return (r or [None])[0] if isinstance(r, list) else None

    def ensure_realm(self, tenant: str, display_name: str, legacy_urls: bool = False) -> Tuple[str, str]:
        """Creates the realm or brings an existing one up to date; returns (realm id, proxy client secret)."""
        existing = self.realm(tenant)
        secret = secrets.token_urlsafe(32)
        if existing is None:
            self.http.call("POST", "/admin/realms", realm_representation(tenant, display_name, self.cfg, secret))
            log.info("keycloak: realm %s created", tenant)
            return tenant, secret
        # existing realm (e.g. m4i of a single-tenant installation): settings, roles and clients, users stay
        rep = realm_representation(tenant, display_name, self.cfg, secret)
        keep = ("id", "realm", "roles", "clients", "displayName")
        if existing.get("displayName"):
            rep["displayName"] = existing["displayName"]
        self.http.call("PUT", f"/admin/realms/{tenant}", {k: v for k, v in rep.items() if k not in keep}
                       | {"displayName": rep["displayName"]})
        for name, desc in ROLES.items():
            status, _ = self.http.call("GET", f"/admin/realms/{tenant}/roles/{name}", ok=(200, 404))
            if status == 404:
                self.http.call("POST", f"/admin/realms/{tenant}/roles", {"name": name, "description": desc})
        self._ensure_client(tenant, frontend_client(tenant, self.cfg, legacy=legacy_urls), keep_secret=True)
        secret = self._ensure_client(tenant, proxy_client(self.cfg, secret), keep_secret=True) or secret
        log.info("keycloak: realm %s up to date", tenant)
        return existing.get("id") or tenant, secret

    def _ensure_client(self, realm: str, rep: dict, keep_secret: bool) -> Optional[str]:
        current = self.client(realm, rep["clientId"])
        if current is None:
            self.http.call("POST", f"/admin/realms/{realm}/clients", rep)
            return rep.get("secret")
        merged = {**current, **{k: v for k, v in rep.items() if k not in ("protocolMappers", "secret")}}
        merged["redirectUris"] = sorted(set(current.get("redirectUris") or []) | set(rep.get("redirectUris") or []))
        self.http.call("PUT", f"/admin/realms/{realm}/clients/{current['id']}", merged)
        names = {m.get("name") for m in current.get("protocolMappers") or []}
        for m in rep.get("protocolMappers") or []:
            if m["name"] not in names:
                self.http.call("POST", f"/admin/realms/{realm}/clients/{current['id']}/protocol-mappers/models", m)
        if not rep.get("publicClient", True) and keep_secret:
            _, s = self.http.call("GET", f"/admin/realms/{realm}/clients/{current['id']}/client-secret")
            return (s or {}).get("value")
        return None

    def ensure_user(self, realm: str, username: str, email: Optional[str], roles: List[str],
                    password: Optional[str] = None, temporary: bool = True) -> Optional[str]:
        """Creates the user if missing (with a temporary password, returned) and grants the roles."""
        _, found = self.http.call("GET", f"/admin/realms/{realm}/users?exact=true&username="
                                         f"{urllib.parse.quote(username)}")
        created_pw = None
        if not found:
            created_pw = password or secrets.token_urlsafe(12)
            body = {"username": username, "enabled": True, "emailVerified": bool(email),
                    "credentials": [{"type": "password", "value": created_pw, "temporary": temporary}]}
            if email:
                body["email"] = email
            self.http.call("POST", f"/admin/realms/{realm}/users", body)
            _, found = self.http.call("GET", f"/admin/realms/{realm}/users?exact=true&username="
                                             f"{urllib.parse.quote(username)}")
        if self.cfg.dry_run and not found:
            return created_pw
        uid = found[0]["id"]
        reps = []
        for r in roles:
            _, rep = self.http.call("GET", f"/admin/realms/{realm}/roles/{r}")
            reps.append({"id": rep["id"], "name": rep["name"]})
        if reps:
            self.http.call("POST", f"/admin/realms/{realm}/users/{uid}/role-mappings/realm", reps)
        return created_pw

    def set_enabled(self, realm: str, enabled: bool) -> None:
        self.http.call("PUT", f"/admin/realms/{realm}", {"enabled": enabled})

    def delete_realm(self, realm: str) -> None:
        self.http.call("DELETE", f"/admin/realms/{realm}", ok=(204, 404))

    def openid_configuration(self, realm: str) -> dict:
        _, r = self.raw.call("GET", f"/realms/{realm}/.well-known/openid-configuration")
        return r

    def export(self, realm: str) -> dict:
        _, r = self.http.call("POST", f"/admin/realms/{realm}/partial-export?exportClients=true"
                                      f"&exportGroupsAndRoles=true")
        return r

    def ensure_entra(self, realm: str, directory_id: str, client_id: str, client_secret: str, alias: str = "entra",
                     role_claim: str = "roles", role_map: Optional[Dict[str, str]] = None,
                     only_entra: bool = False) -> None:
        """Microsoft Entra ID as identity provider of the realm; Entra app roles become Aurelius roles."""
        issuer = f"https://login.microsoftonline.com/{directory_id}/v2.0"
        base = f"https://login.microsoftonline.com/{directory_id}/oauth2/v2.0"
        rep = {"alias": alias, "displayName": "Microsoft Entra ID", "providerId": "oidc", "enabled": True,
               "trustEmail": True, "firstBrokerLoginFlowAlias": "first broker login", "storeToken": False,
               "config": {"issuer": issuer, "authorizationUrl": f"{base}/authorize", "tokenUrl": f"{base}/token",
                          "jwksUrl": f"https://login.microsoftonline.com/{directory_id}/discovery/v2.0/keys",
                          "logoutUrl": f"{base}/logout", "useJwksUrl": "true", "validateSignature": "true",
                          "clientId": client_id, "clientSecret": client_secret, "clientAuthMethod": "client_secret_post",
                          "defaultScope": "openid profile email", "syncMode": "FORCE", "pkceEnabled": "true",
                          "pkceMethod": "S256"}}
        status, _ = self.http.call("GET", f"/admin/realms/{realm}/identity-provider/instances/{alias}", ok=(200, 404))
        if status == 404:
            self.http.call("POST", f"/admin/realms/{realm}/identity-provider/instances", rep)
        else:
            self.http.call("PUT", f"/admin/realms/{realm}/identity-provider/instances/{alias}", rep)
        role_map = role_map or {r: r for r in ROLES}
        _, mappers = self.http.call("GET", f"/admin/realms/{realm}/identity-provider/instances/{alias}/mappers")
        have = {m["name"] for m in mappers or []}
        for app_role, aurelius_role in role_map.items():
            name = f"{app_role} -> {aurelius_role}"
            if name in have:
                continue
            self.http.call("POST", f"/admin/realms/{realm}/identity-provider/instances/{alias}/mappers", {
                "name": name, "identityProviderAlias": alias, "identityProviderMapper": "oidc-role-idp-mapper",
                "config": {"syncMode": "FORCE", "claim": role_claim, "claim.value": app_role,
                           "role": aurelius_role}})
        if only_entra:
            # the login page goes straight to Entra ID (identity provider redirector)
            _, execs = self.http.call("GET", f"/admin/realms/{realm}/authentication/flows/browser/executions")
            for ex in execs or []:
                if ex.get("providerId") == "identity-provider-redirector":
                    cfg_body = {"alias": f"{alias}-default", "config": {"defaultProvider": alias}}
                    self.http.call("POST", f"/admin/realms/{realm}/authentication/executions/{ex['id']}/config",
                                   cfg_body, ok=(201, 204, 409))
        log.info("keycloak: Entra ID (%s) connected to realm %s; redirect URI for the Entra app: %s", directory_id,
                 realm, f"{self.cfg.public_url}/{self.cfg.ns}/auth/realms/{realm}/broker/{alias}/endpoint")


# --------------------------------------------------------------------------------------------------- Elasticsearch
def pyatlas_key_descriptor(tenant: str) -> dict:
    return {f"aurelius-{tenant}-pyatlas": {"indices": [{"names": [f"aurelius_{tenant}_*"], "privileges": ["all"]}]}}


def kibana_key_descriptor(tenant: str, all_tenants: bool = False) -> dict:
    names = ["aurelius_*", "logs-aurelius.*-*"] if all_tenants else [f"aurelius_{tenant}_*",
                                                                     f"logs-aurelius.*-{tenant}"]
    if all_tenants:
        names.append("aurelius_platform_*")
    return {f"aurelius-{tenant}-kibana": {
        "indices": [{"names": names, "privileges": ["read", "view_index_metadata"]}],
        "applications": [{"application": "kibana-.kibana", "privileges": ["space_all"],
                          "resources": [f"space:{tenant}"]}]}}


def logs_pipeline() -> dict:
    """Routes a log line of the shipper to ``logs-aurelius.<source>-<tenant>``; a missing or unknown tenant goes
    to ``platform``.  The tenant is checked against the registry (enrich policies), never taken on trust."""
    return {"description": "Aurelius logs: tenant check and routing to logs-aurelius.<source>-<tenant>",
            "processors": [
                # compose service of the container (copied by the shipper)
                {"set": {"field": "aurelius.source", "value": "{{{aurelius.service}}}", "ignore_empty_value": True}},
                {"script": {"lang": "painless", "source": """
                    if (ctx.aurelius == null) { ctx.aurelius = [:]; }
                    def s = ctx.aurelius.source;
                    if (s == 'reverse-proxy') { ctx.aurelius.source = 'proxy'; }
                    else if (s != 'pyatlas' && s != 'keycloak') { ctx.aurelius.source = 'other'; }
                    if (ctx.tenant instanceof String && (ctx.tenant == '-' || ctx.tenant == '')) { ctx.remove('tenant'); }
                """}},
                # Keycloak login events: "type=LOGIN, realmId=acme, clientId=..., username=..."
                {"kv": {"if": "ctx.loggerName == 'org.keycloak.events' && ctx.message != null",
                        "field": "message", "target_field": "kc", "field_split": ", ", "value_split": "=",
                        "ignore_failure": True}},
                {"enrich": {"if": "ctx.aurelius.source == 'keycloak' && ctx.kc?.realmId != null",
                            "policy_name": ENRICH_REALMS, "field": "kc.realmId", "target_field": "aurelius.realm",
                            "ignore_missing": True}},
                {"set": {"if": "ctx.aurelius?.realm?.id != null", "field": "tenant", "copy_from": "aurelius.realm.id"}},
                {"enrich": {"if": "ctx.tenant != null", "policy_name": ENRICH_TENANTS, "field": "tenant",
                            "target_field": "aurelius.registry", "ignore_missing": True}},
                {"script": {"lang": "painless", "source": """
                    if (ctx.tenant == null || ctx.aurelius?.registry?.id != ctx.tenant) { ctx.tenant = 'platform'; }
                    ctx.aurelius.remove('registry'); ctx.aurelius.remove('realm');
                """}},
                {"remove": {"field": ["authorization", "Authorization", "cookie", "Cookie", "password", "token",
                                      "kc.password", "kc.token"], "ignore_missing": True}},
                {"set": {"field": "aurelius.dataset", "value": "aurelius.{{{aurelius.source}}}"}},
                {"reroute": {"dataset": "{{aurelius.dataset}}", "namespace": "{{tenant}}"}},
            ],
            "on_failure": [{"set": {"field": "error.message", "value": "{{{_ingest.on_failure_message}}}"}},
                           {"set": {"field": "tenant", "value": "platform"}},
                           {"reroute": {"dataset": "aurelius.other", "namespace": "platform"}}]}


def logs_template(name: str, pattern: str, retention_days: int, priority: int) -> dict:
    return {"index_patterns": [pattern], "priority": priority, "data_stream": {},
            "composed_of": ["logs@mappings", "ecs@mappings"], "ignore_missing_component_templates": ["ecs@mappings"],
            "template": {"lifecycle": {"data_retention": f"{retention_days}d"},
                         "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                         "mappings": {"properties": {"tenant": {"type": "keyword"},
                                                     "status": {"type": "long"},
                                                     "duration_ms": {"type": "float"},
                                                     "path": {"type": "keyword"}, "user": {"type": "keyword"}}}},
            "_meta": {"managed_by": "aurelius-admin", "name": name}}


class Elastic:
    def __init__(self, cfg: Config, transport: Transport):
        self.cfg = cfg
        token = base64.b64encode(f"{cfg.es_username}:{cfg.es_password}".encode()).decode()
        self.http = Http(cfg.es_url, transport, lambda: {"Authorization": f"Basic {token}"}, cfg.dry_run,
                         "elasticsearch")

    # platform
    def ensure_registry(self) -> None:
        status, _ = self.http.call("HEAD", f"/{self.cfg.registry_index}", ok=(200, 404))
        if status == 404:
            self.http.call("PUT", f"/{self.cfg.registry_index}", {
                "settings": {"number_of_shards": 1, "number_of_replicas": 0}, "mappings": REGISTRY_MAPPING})
        else:
            self.http.call("PUT", f"/{self.cfg.registry_index}/_mapping", REGISTRY_MAPPING)
        # settings of the platform (operators' realm): stored, not searchable
        status, _ = self.http.call("HEAD", f"/{self.cfg.settings_index}", ok=(200, 404))
        if status == 404:
            self.http.call("PUT", f"/{self.cfg.settings_index}", {
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {"dynamic": False, "properties": {"realm": {"type": "keyword"}}}})

    def ensure_platform_security(self) -> None:
        c = self.cfg
        if c.kibana_system_password:
            self.http.call("POST", "/_security/user/kibana_system/_password", {"password": c.kibana_system_password})
        # pyatlas itself: the tenant registry and its readiness check; the tenants' data only with their own keys
        self.http.call("PUT", "/_security/role/aurelius_pyatlas", {
            "cluster": ["cluster:monitor/main"],
            "indices": [{"names": [f"{c.platform_prefix}_*"], "privileges": ["read", "view_index_metadata"]}]})
        if c.pyatlas_es_password:
            self.http.call("PUT", "/_security/user/aurelius_pyatlas", {
                "password": c.pyatlas_es_password, "roles": ["aurelius_pyatlas"],
                "full_name": "pyatlas (tenant registry only; tenants use their own API keys)"})
        self.http.call("PUT", "/_security/role/aurelius_filebeat", {
            "cluster": ["monitor", "read_pipeline"],
            "indices": [{"names": ["logs-aurelius.*"], "privileges": ["create_doc", "auto_configure"]}]})
        if c.filebeat_password:
            self.http.call("PUT", "/_security/user/aurelius_filebeat", {
                "password": c.filebeat_password, "roles": ["aurelius_filebeat"], "full_name": "Aurelius log shipper"})

    def ensure_logging(self) -> None:
        c = self.cfg
        self.http.call("PUT", "/_index_template/logs-aurelius",
                       logs_template("logs-aurelius", "logs-aurelius.*-*", c.log_retention_days, 200))
        for name, match in ((ENRICH_TENANTS, "id"), (ENRICH_REALMS, "realmId")):
            status, cur = self.http.call("GET", f"/_enrich/policy/{name}", ok=(200, 404))
            if not (status == 200 and (cur or {}).get("policies")):
                self.http.call("PUT", f"/_enrich/policy/{name}", {"match": {
                    "indices": c.registry_index, "match_field": match, "enrich_fields": ["id", "status"],
                    "query": {"term": {"status": ACTIVE}}}})
        self.execute_enrich()
        self.http.call("PUT", f"/_ingest/pipeline/{LOGS_PIPELINE}", logs_pipeline())

    def execute_enrich(self) -> None:
        for name in (ENRICH_TENANTS, ENRICH_REALMS):
            self.http.call("POST", f"/_enrich/policy/{name}/_execute?wait_for_completion=true", ok=(200, 404))

    # tenants
    def api_key(self, name: str, descriptors: dict, tenant: str) -> Tuple[str, str]:
        _, r = self.http.call("POST", "/_security/api_key", {
            "name": name, "role_descriptors": descriptors,
            "metadata": {"aurelius_tenant": tenant, "managed_by": "aurelius-admin"}})
        return r.get("id", "dry-run"), r.get("encoded", base64.b64encode(b"dry-run:key").decode())

    def invalidate_keys(self, ids: List[str]) -> None:
        ids = [i for i in ids if i]
        if ids:
            self.http.call("DELETE", "/_security/api_key", {"ids": ids}, ok=(200, 404))

    def key_valid(self, encoded: Optional[str]) -> bool:
        if not encoded:
            return False
        status, _ = self.http.transport("GET", self.cfg.es_url + "/_security/_authenticate",
                                        {"Authorization": f"ApiKey {encoded}"}, None)
        return status == 200

    def tenant_logs_template(self, tenant: str, retention_days: int) -> None:
        self.http.call("PUT", f"/_index_template/logs-aurelius-{tenant}",
                       logs_template(f"logs-aurelius-{tenant}", f"logs-aurelius.*-{tenant}", retention_days, 210))

    def delete_tenant_data(self, tenant: str) -> None:
        self.http.call("DELETE", f"/aurelius_{tenant}_*?expand_wildcards=all&allow_no_indices=true", ok=(200, 404))
        self.http.call("DELETE", f"/_data_stream/logs-aurelius.*-{tenant}", ok=(200, 404))
        self.http.call("DELETE", f"/_index_template/logs-aurelius-{tenant}", ok=(200, 404))

    def copy_indices(self, source_prefix: str, tenant: str) -> List[str]:
        """Copies ``<source_prefix>_*`` (a single-tenant installation) to ``aurelius_<tenant>_*`` (the source
        stays; delete it once the tenant works)."""
        _, idx = self.http.call("GET", f"/{source_prefix}_*?expand_wildcards=open", ok=(200, 404))
        copied = []
        for name, meta in sorted((idx or {}).items()):
            if not name.startswith(f"{source_prefix}_"):
                continue
            target = f"aurelius_{tenant}_{name[len(source_prefix) + 1:]}"
            status, _ = self.http.call("HEAD", f"/{target}", ok=(200, 404))
            if status == 200:
                log.info("elasticsearch: %s exists, not copied again", target)
                continue
            settings = {k: v for k, v in (meta.get("settings", {}).get("index", {}) or {}).items()
                        if k in ("analysis", "mapping", "number_of_shards")}
            self.http.call("PUT", f"/{target}", {"settings": settings, "mappings": meta.get("mappings", {})})
            self.http.call("POST", "/_reindex?wait_for_completion=true&refresh=true",
                           {"source": {"index": name}, "dest": {"index": target}})
            copied.append(target)
            log.info("elasticsearch: %s copied to %s", name, target)
        return copied

    def export_index(self, index: str) -> List[dict]:
        out, after = [], None
        while True:
            body = {"size": 1000, "sort": [{"_doc": "asc"}], "query": {"match_all": {}}}
            if after:
                body["search_after"] = after
            status, r = self.http.call("POST", f"/{index}/_search", body, ok=(200, 404))
            hits = (r or {}).get("hits", {}).get("hits", []) if status == 200 else []
            if not hits:
                return out
            out += [{"_id": h["_id"], "_source": h["_source"]} for h in hits]
            after = hits[-1]["sort"]

    def tenant_indices(self, tenant: str) -> List[str]:
        _, r = self.http.call("GET", f"/_cat/indices/aurelius_{tenant}_*?format=json&h=index", ok=(200, 404))
        return sorted(x["index"] for x in r or [] if isinstance(x, dict))


# --------------------------------------------------------------------------------------------------- Kibana
class Kibana:
    def __init__(self, cfg: Config, transport: Transport):
        self.cfg = cfg
        token = base64.b64encode(f"{cfg.es_username}:{cfg.es_password}".encode()).decode()
        self.http = Http(cfg.kibana_url, transport, lambda: {"Authorization": f"Basic {token}", "kbn-xsrf": "aurelius"},
                         cfg.dry_run, "kibana")

    def wait(self, timeout: float = 600) -> None:
        t0 = time.time()
        while True:
            try:
                status, r = self.http.call("GET", "/api/status", ok=None)
                if status == 200 and (r or {}).get("status", {}).get("overall", {}).get("level") == "available":
                    return
            except OSError:
                pass
            if time.time() - t0 > timeout:
                raise AdminError("Kibana did not become available")
            time.sleep(5)

    def ensure_space(self, space: str, name: str, description: str) -> None:
        body = {"id": space, "name": name, "description": description, "disabledFeatures": [],
                "initials": space[:2].upper()}
        status, _ = self.http.call("GET", f"/api/spaces/space/{space}", ok=(200, 404))
        if status == 404:
            self.http.call("POST", "/api/spaces/space", body)
        else:
            self.http.call("PUT", f"/api/spaces/space/{space}", body)

    def import_objects(self, space: str, objects: List[dict]) -> None:
        from .kibana_objects import ndjson
        boundary = "aurelius" + secrets.token_hex(8)
        payload = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"aurelius.ndjson\"\r\n"
                   f"Content-Type: application/ndjson\r\n\r\n{ndjson(objects)}\r\n--{boundary}--\r\n").encode()
        _, r = self.http.call("POST", f"/s/{space}/api/saved_objects/_import?overwrite=true", raw=payload,
                              content_type=f"multipart/form-data; boundary={boundary}")
        if not self.cfg.dry_run and not (r or {}).get("success"):
            raise AdminError(f"kibana: import into space {space} failed: {str(r)[:500]}")
        # default data view through the public data views API; the advanced settings API is internal in Kibana 9
        # (the dashboards bring their own time range), so it is tried but not required
        self.http.call("POST", f"/s/{space}/api/data_views/default",
                       {"data_view_id": "pyatlas-entities", "force": True}, ok=(200, 404))
        status, _ = self.http.call("POST", f"/s/{space}/api/kibana/settings", {"changes": {
            "defaultRoute": "/app/dashboards",
            "timepicker:timeDefaults": json.dumps({"from": "now-30d", "to": "now"})}}, ok=None)
        if status != 200:
            log.info("kibana: advanced settings of space %s not set (HTTP %s); defaults stay", space, status)

    def delete_space(self, space: str) -> None:
        self.http.call("DELETE", f"/api/spaces/space/{space}", ok=(204, 404))


# --------------------------------------------------------------------------------------------------- proxy files
def issuer_filename(issuer: str) -> str:
    """mod_auth_openidc's OIDCMetadataDir file name of an issuer: scheme removed, URL-encoded."""
    s = issuer
    for scheme in ("https://", "http://"):
        if s.startswith(scheme):
            s = s[len(scheme):]
            break
    return urllib.parse.quote(s.rstrip("/"), safe="")


class ProxyFiles:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.dir = cfg.tenants_dir

    def _write(self, path: Path, text: str) -> None:
        if self.cfg.dry_run:
            log.info("[dry-run] write %s", path)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.chmod(tmp, 0o644)          # read by the proxy's worker user
        tmp.replace(path)

    def set_realm(self, realm: str, provider_metadata: dict, client_secret: str) -> None:
        base = self.dir / "oidc" / issuer_filename(self.cfg.issuer(realm))
        self._write(Path(str(base) + ".provider"), json.dumps(provider_metadata))
        self._write(Path(str(base) + ".client"), json.dumps({
            "client_id": PROXY_CLIENT, "client_secret": client_secret,
            "token_endpoint_auth_method": "client_secret_basic"}))
        self._write(Path(str(base) + ".conf"), json.dumps({"scope": "openid", "response_type": "code"}))

    def set_realm_if_changed(self, realm: str, provider_metadata: dict, client_secret: str) -> int:
        base = self.dir / "oidc" / issuer_filename(self.cfg.issuer(realm))
        try:
            same = json.loads(Path(str(base) + ".client").read_text(encoding="utf-8")).get("client_secret") == \
                client_secret and json.loads(Path(str(base) + ".provider").read_text(encoding="utf-8")) == \
                provider_metadata
        except (OSError, ValueError):
            same = False
        if same:
            return 0
        self.set_realm(realm, provider_metadata, client_secret)
        return 1

    def retain_realms(self, realms: set) -> None:
        """Removes the login provider files of realms that are no longer tenants (deleted or suspended)."""
        keep = {issuer_filename(self.cfg.issuer(r)) for r in realms}
        folder = self.dir / "oidc"
        if self.cfg.dry_run or not folder.is_dir():
            return
        for f in folder.iterdir():
            if f.suffix in (".provider", ".client", ".conf") and f.stem not in keep:
                f.unlink(missing_ok=True)

    def write_keys(self, keys: Dict[str, str]) -> None:
        text = "# tenant  Kibana API key - written by aurelius-admin, read by the reverse proxy (RewriteMap)\n" + \
            "".join(f"{t} {k}\n" for t, k in sorted(keys.items()))
        self._write(self.dir / "kibana-keys.txt", text)

    def remove_realm(self, realm: str) -> None:
        base = str(self.dir / "oidc" / issuer_filename(self.cfg.issuer(realm)))
        for ext in (".provider", ".client", ".conf"):
            if not self.cfg.dry_run:
                Path(base + ext).unlink(missing_ok=True)

    def keys(self) -> Dict[str, str]:
        p = self.dir / "kibana-keys.txt"
        out = {}
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if len(parts) == 2 and not line.startswith("#"):
                    out[parts[0]] = parts[1]
        return out

    def set_key(self, tenant: str, key: Optional[str]) -> None:
        keys = self.keys()
        if key is None:
            keys.pop(tenant, None)
        else:
            keys[tenant] = key
        self.write_keys(keys)


# --------------------------------------------------------------------------------------------------- commands
@dataclass
class Admin:
    cfg: Config
    transport: Transport = urllib_transport
    es_client: Any = None
    out: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.kc = Keycloak(self.cfg, self.transport)
        self.es = Elastic(self.cfg, self.transport)
        self.kibana = Kibana(self.cfg, self.transport)
        self.files = ProxyFiles(self.cfg)

    def say(self, msg: str) -> None:
        self.out.append(msg)
        print(msg, flush=True)

    def _on(self, part: str) -> bool:
        return part not in self.cfg.skip

    # registry through the platform (elastic) credentials
    def _registry(self):
        from .config import Settings
        from .tenancy import TenantRegistry
        if self.es_client is None:
            from elasticsearch import AsyncElasticsearch
            self.es_client = AsyncElasticsearch(self.cfg.es_url, basic_auth=(self.cfg.es_username,
                                                                              self.cfg.es_password))
        return TenantRegistry(self.es_client, Settings(tenant_platform_prefix=self.cfg.platform_prefix),
                              cache_secs=0)

    async def wait_ready(self, timeout: float) -> None:
        """Waits until Elasticsearch (with the configured user) and Keycloak (admin login) answer."""
        t0 = time.time()
        pending = [p for p in ("elasticsearch", "keycloak") if self._on(p)]
        while pending:
            part = pending[0]
            try:
                if part == "elasticsearch":
                    status, _ = self.es.http.call("GET", "/_cluster/health", ok=None)
                    ready = status == 200
                else:
                    self.kc._token = None
                    self.kc._auth()
                    ready = True
            except (AdminError, OSError, KeyError, ValueError):
                ready = False
            if ready:
                self.say(f"{part} ready")
                pending.pop(0)
                continue
            if time.time() - t0 > timeout:
                raise AdminError(f"{part} did not become ready within {timeout:.0f}s")
            await asyncio.sleep(5)

    async def close(self) -> None:
        if self.es_client is not None and hasattr(self.es_client, "close"):
            await self.es_client.close()

    # ---------------------------------------------------------------- platform
    async def platform_init(self) -> None:
        c = self.cfg
        settings = await self._get_settings() if self._on("elasticsearch") and not c.dry_run else {}
        if self._on("elasticsearch"):
            self.es.ensure_registry()
            self.es.ensure_platform_security()
            self.es.ensure_logging()
            self.say("elasticsearch: registry, users (kibana_system, aurelius_pyatlas, aurelius_filebeat), "
                     "log routing ready")
        realm = c.platform_realm
        if self._on("keycloak"):
            _, secret = self.kc.ensure_realm(realm, "Aurelius platform operators")
            pw = self.kc.ensure_user(realm, "operator", None, ["ROLE_ADMIN"], c.operator_password or None,
                                     temporary=not c.operator_password)
            if pw and not c.operator_password:
                self.say(f"keycloak: user 'operator' of realm {realm} created, temporary password: {pw}")
            settings["proxyClientSecret"] = secret
            if self._on("proxy"):
                self.files.set_realm(realm, self.kc.openid_configuration(realm), secret)
        if self._on("kibana") and self._on("elasticsearch"):
            from .kibana_objects import saved_objects
            self.kibana.wait()
            self.kibana.ensure_space(realm, "Aurelius platform", "All tenants (operators only)")
            self.kibana.import_objects(realm, saved_objects("aurelius_*", "*", platform=True))
            current = settings.get("kibanaApiKey") or self.files.keys().get(realm)
            if not self.es.key_valid(current):
                self.es.invalidate_keys([settings.get("kibanaApiKeyId")])
                settings["kibanaApiKeyId"], current = self.es.api_key(
                    f"aurelius-{realm}-kibana", kibana_key_descriptor(realm, all_tenants=True), realm)
            settings["kibanaApiKey"] = current
            if self._on("proxy"):
                self.files.set_key(realm, current)
            self.say(f"kibana: space {realm} with the dashboards of all tenants")
        if self._on("elasticsearch") and not c.dry_run:
            await self._put_settings(settings)
        self.say("platform ready")

    # the operators' realm is not a tenant: its proxy secret and Kibana key live in <platform prefix>_settings
    async def _get_settings(self) -> dict:
        from elasticsearch import NotFoundError
        self._registry()
        try:
            r = await self.es_client.get(index=self.cfg.settings_index, id="platform")
            return dict(r["_source"])
        except NotFoundError:
            return {}

    async def _put_settings(self, settings: dict) -> None:
        self._registry()
        await self.es_client.index(index=self.cfg.settings_index, id="platform",
                                   document={**settings, "realm": self.cfg.platform_realm}, refresh="wait_for")

    # ---------------------------------------------------------------- tenants
    async def tenant_create(self, tenant: str, name: Optional[str] = None, admin_user: Optional[str] = None,
                            admin_email: Optional[str] = None, sample_data: Optional[str] = None,
                            migrate_from: Optional[str] = None, retention_days: Optional[int] = None,
                            legacy_urls: bool = False) -> dict:
        check_tenant_id(tenant)
        if tenant == self.cfg.platform_realm:
            raise AdminError(f"{tenant} is the operators' realm, not a tenant")
        reg = self._registry()
        rec = await reg.get(tenant, cached=False) or {}
        rec = {**rec, "id": tenant, "name": name or rec.get("name") or tenant, "realm": tenant,
               "status": rec.get("status") if rec.get("status") in (ACTIVE, "suspended") else "provisioning"}
        if retention_days:
            rec["retentionDays"] = retention_days
        if not self.cfg.dry_run:
            rec = await reg.put(rec)
        # 2. realm
        if self._on("keycloak"):
            realm_id, secret = self.kc.ensure_realm(tenant, rec["name"], legacy_urls=legacy_urls)
            rec["realmId"] = realm_id
            rec["proxyClientSecret"] = secret
            if admin_user:
                pw = self.kc.ensure_user(tenant, admin_user, admin_email, ["ROLE_ADMIN", "DATA_STEWARD"])
                if pw:
                    self.say(f"keycloak: user {admin_user} created in realm {tenant}, temporary password: {pw}")
            if self._on("proxy"):
                self.files.set_realm(tenant, self.kc.openid_configuration(tenant), secret)
            self.say(f"keycloak: realm {tenant} ready (login at {self.cfg.public_url}/{self.cfg.ns}/{tenant}/atlas/)")
        # 3. data, keys
        if self._on("elasticsearch"):
            if migrate_from:
                copied = self.es.copy_indices(migrate_from, tenant)
                self.say(f"elasticsearch: {len(copied)} indices of {migrate_from}_* copied to aurelius_{tenant}_*")
            if not self.es.key_valid(rec.get("esApiKey")):
                self.es.invalidate_keys([rec.get("esApiKeyId")])
                rec["esApiKeyId"], rec["esApiKey"] = self.es.api_key(f"aurelius-{tenant}-pyatlas",
                                                                     pyatlas_key_descriptor(tenant), tenant)
            self.es.tenant_logs_template(tenant, retention_days or rec.get("retentionDays") or
                                         self.cfg.log_retention_days)
            self.say(f"elasticsearch: API key of pyatlas for aurelius_{tenant}_* ready")
        # 4. Kibana
        if self._on("kibana") and self._on("elasticsearch"):
            from .kibana_objects import saved_objects
            self.kibana.wait()
            self.kibana.ensure_space(tenant, rec["name"], f"Aurelius of {rec['name']}")
            self.kibana.import_objects(tenant, saved_objects(f"aurelius_{tenant}", tenant))
            current = rec.get("kibanaApiKey") or self.files.keys().get(tenant)
            if not self.es.key_valid(current):
                self.es.invalidate_keys([rec.get("kibanaApiKeyId")])
                rec["kibanaApiKeyId"], current = self.es.api_key(f"aurelius-{tenant}-kibana",
                                                                 kibana_key_descriptor(tenant), tenant)
            rec["kibanaApiKey"] = current
            if self._on("proxy"):
                self.files.set_key(tenant, current)
            self.say(f"kibana: space {tenant} with the dashboards (open {self.cfg.public_url}/{self.cfg.ns}/"
                     f"{tenant}/kibana/)")
        if rec["status"] == "provisioning":
            rec["status"] = ACTIVE
        if not self.cfg.dry_run:
            rec = await reg.put(rec)
        if self._on("elasticsearch"):
            self.es.execute_enrich()          # log lines of the new tenant are routed from now on
        if sample_data:
            await self._import_sample(tenant, rec, sample_data)
        self.say(f"tenant {tenant} {rec['status']}")
        return rec

    async def _import_sample(self, tenant: str, rec: dict, path: str) -> None:
        from .config import Settings
        from .services import Services
        from .store.es import make_client
        from .tenancy import tenant_settings
        base = Settings(es_hosts=self.cfg.es_url, es_api_key=rec.get("esApiKey"), aurelius_quality_seed="")
        settings = tenant_settings(base, tenant)
        client = make_client(settings)
        try:
            services = Services(client, settings, tenant=tenant)
            await services.start(retention=False)
            res = await services.impexp.import_zip(Path(path).read_bytes(), {"options": {"fileName": path}}, "admin")
            await services.stop()
            self.say(f"sample data imported into {tenant}: {res['operationStatus']}")
        finally:
            await client.close()

    async def tenant_status(self, tenant: str, status: str) -> None:
        reg = self._registry()
        rec = await reg.get(tenant, cached=False)
        if rec is None:
            raise AdminError(f"unknown tenant {tenant}")
        if self._on("keycloak"):
            self.kc.set_enabled(tenant, status == ACTIVE)
        if not self.cfg.dry_run:
            await reg.update(tenant, status=status)
        if self._on("elasticsearch"):
            self.es.execute_enrich()
        self.say(f"tenant {tenant} {status}")

    async def tenant_delete(self, tenant: str) -> None:
        check_tenant_id(tenant)
        reg = self._registry()
        rec = await reg.get(tenant, cached=False) or {"id": tenant}
        if not self.cfg.dry_run and rec.get("status"):
            await reg.update(tenant, status="deleting")
        if self._on("proxy"):
            self.files.set_key(tenant, None)
            self.files.remove_realm(tenant)
        if self._on("kibana"):
            self.kibana.delete_space(tenant)
        if self._on("elasticsearch"):
            self.es.invalidate_keys([rec.get("esApiKeyId"), rec.get("kibanaApiKeyId")])
            self.es.delete_tenant_data(tenant)
        if self._on("keycloak"):
            self.kc.delete_realm(tenant)
        if not self.cfg.dry_run:
            await reg.delete(tenant)
        if self._on("elasticsearch"):
            self.es.execute_enrich()
        self.say(f"tenant {tenant} deleted")

    async def tenant_export(self, tenant: str, out: Path) -> None:
        import zipfile
        rec = await self._registry().get(tenant, cached=False)
        if rec is None:
            raise AdminError(f"unknown tenant {tenant}")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            safe = {k: v for k, v in rec.items() if k not in SECRET_FIELDS}
            z.writestr("tenant.json", json.dumps(safe, indent=1))
            if self._on("keycloak"):
                z.writestr("keycloak-realm.json", json.dumps(self.kc.export(tenant), indent=1))
            if self._on("elasticsearch"):
                names = self.es.tenant_indices(tenant)
                names += [f"logs-aurelius.{s}-{tenant}" for s in LOG_SOURCES]
                for idx in names:
                    docs = self.es.export_index(idx)
                    if docs:
                        z.writestr(f"elasticsearch/{idx}.ndjson", "".join(json.dumps(d) + "\n" for d in docs))
        self.say(f"tenant {tenant} exported to {out}")

    async def tenant_list(self) -> List[dict]:
        recs = await self._registry().list()
        for r in recs:
            self.say(f"{r['id']:<20} {r.get('status', ''):<12} {r.get('name', '')}")
        return recs


# --------------------------------------------------------------------------------------------------- proxy sync
async def proxy_sync(admin: "Admin", files: "ProxyFiles") -> Dict[str, int]:
    """Writes the reverse proxy's tenant files (Kibana login providers, Kibana keys) from the tenant registry: every
    active tenant and the operators' realm.  Runs next to the proxy (Kubernetes: a sidecar with a shared emptyDir), so
    the proxy needs no shared volume with the admin jobs; needs only read access to the registry (the pyatlas user)
    and Keycloak's public OpenID configuration."""
    cfg = admin.cfg
    if not cfg.dry_run and not (files.dir / "kibana-keys.txt").exists():
        (files.dir / "oidc").mkdir(parents=True, exist_ok=True)
        files.write_keys({})                               # the proxy can start before the first tenant exists
    wanted: Dict[str, Tuple[str, Optional[str]]] = {}      # realm -> (proxy client secret, kibana key)
    from elasticsearch import NotFoundError
    try:
        records = await admin._registry().list()
    except NotFoundError:          # no platform yet (aurelius-init has not run): the proxy starts without tenants
        records = []
    for rec in records:
        if rec.get("status") == ACTIVE and rec.get("proxyClientSecret"):
            wanted[rec.get("realm") or rec["id"]] = (rec["proxyClientSecret"], rec.get("kibanaApiKey"))
    settings = await admin._get_settings()
    if settings.get("proxyClientSecret"):
        wanted[cfg.platform_realm] = (settings["proxyClientSecret"], settings.get("kibanaApiKey"))
    written = 0
    for realm, (secret, _key) in sorted(wanted.items()):
        try:
            metadata = admin.kc.openid_configuration(realm)
        except (AdminError, OSError) as e:
            log.warning("proxy sync: realm %s not reachable: %s", realm, e)
            continue
        written += files.set_realm_if_changed(realm, metadata, secret)
    files.retain_realms(set(wanted))
    keys = {realm: key for realm, (_s, key) in wanted.items() if key}
    if keys != files.keys():
        files.write_keys(keys)
        written += 1
    return {"realms": len(wanted), "changed": written}


# --------------------------------------------------------------------------------------------------- CLI
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="aurelius-admin", description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="show what would change")
    ap.add_argument("--skip", default="", help="comma separated: keycloak, elasticsearch, kibana, proxy")
    ap.add_argument("--wait", type=float, default=0, metavar="SECONDS",
                    help="first wait up to SECONDS until Elasticsearch and Keycloak answer (installation jobs)")
    sub = ap.add_subparsers(dest="area", required=True)
    plat = sub.add_parser("platform").add_subparsers(dest="cmd", required=True)
    plat.add_parser("init", help="registry, users, log routing, operators' realm and Kibana space")
    px = sub.add_parser("proxy").add_subparsers(dest="cmd", required=True)
    ps = px.add_parser("sync", help="write the proxy's tenant files from the registry (Kubernetes sidecar)")
    ps.add_argument("--loop", type=float, default=0, metavar="SECONDS", help="repeat every SECONDS (0 = once)")
    ten = sub.add_parser("tenant").add_subparsers(dest="cmd", required=True)
    c = ten.add_parser("create", help="create a tenant or bring it up to date")
    c.add_argument("tenant")
    c.add_argument("--name")
    c.add_argument("--admin-user")
    c.add_argument("--admin-email")
    c.add_argument("--sample-data", metavar="ZIP")
    c.add_argument("--migrate-from", metavar="PREFIX", help="copy the indices of a single-tenant installation")
    c.add_argument("--retention-days", type=int)
    c.add_argument("--legacy-urls", action="store_true", help="keep /<ns>/atlas/ as redirect URL (default tenant)")
    ten.add_parser("list")
    for name in ("show", "suspend", "resume"):
        ten.add_parser(name).add_argument("tenant")
    d = ten.add_parser("delete")
    d.add_argument("tenant")
    d.add_argument("--yes", action="store_true", help="really delete realm, data, logs, space and keys")
    x = ten.add_parser("export")
    x.add_argument("tenant")
    x.add_argument("--out", required=True)
    e = ten.add_parser("entra", help="connect the tenant's Microsoft Entra ID")
    e.add_argument("tenant")
    e.add_argument("--directory-id", required=True)
    e.add_argument("--client-id", required=True)
    e.add_argument("--client-secret", required=True)
    e.add_argument("--alias", default="entra")
    e.add_argument("--role-claim", default="roles")
    e.add_argument("--map", action="append", default=[], metavar="APPROLE=AURELIUSROLE",
                   help="Entra app role to Aurelius role (default: same names)")
    e.add_argument("--only-entra", action="store_true", help="login page goes straight to Entra ID")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cfg = Config.from_env(dry_run=args.dry_run, skip=tuple(s.strip() for s in args.skip.split(",") if s.strip()))
    admin = Admin(cfg)

    async def run():
        try:
            if args.wait:
                await admin.wait_ready(args.wait)
            if args.area == "platform":
                await admin.platform_init()
            elif args.area == "proxy":
                while True:
                    try:
                        res = await proxy_sync(admin, admin.files)
                        if res["changed"]:
                            log.info("proxy sync: %s", res)
                    except Exception as e:  # noqa: BLE001 - keep the sidecar running
                        if not args.loop:
                            raise
                        log.warning("proxy sync failed: %s", e)
                    if not args.loop:
                        break
                    await asyncio.sleep(args.loop)
            elif args.cmd == "create":
                await admin.tenant_create(args.tenant, args.name, args.admin_user, args.admin_email, args.sample_data,
                                          args.migrate_from, args.retention_days, args.legacy_urls)
            elif args.cmd == "list":
                await admin.tenant_list()
            elif args.cmd == "show":
                rec = await admin._registry().get(args.tenant, cached=False)
                print(json.dumps({k: v for k, v in (rec or {}).items() if k not in SECRET_FIELDS}, indent=1))
            elif args.cmd in ("suspend", "resume"):
                await admin.tenant_status(args.tenant, "suspended" if args.cmd == "suspend" else ACTIVE)
            elif args.cmd == "delete":
                if not args.yes:
                    raise AdminError("deleting removes the realm, all data, logs, the Kibana space and keys of "
                                     f"{args.tenant}; add --yes (export it first: tenant export)")
                await admin.tenant_delete(args.tenant)
            elif args.cmd == "export":
                await admin.tenant_export(args.tenant, Path(args.out))
            elif args.cmd == "entra":
                role_map = dict(m.split("=", 1) for m in args.map) or None
                admin.kc.ensure_entra(args.tenant, args.directory_id, args.client_id, args.client_secret, args.alias,
                                      args.role_claim, role_map, args.only_entra)
        finally:
            await admin.close()
    try:
        asyncio.run(run())
    except AdminError as e:
        print(f"aurelius-admin: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
