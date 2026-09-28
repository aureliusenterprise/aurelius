"""Server configuration.

All settings can be supplied as environment variables prefixed with ``PYATLAS_``
(for example ``PYATLAS_ES_HOSTS=http://es1:9200,http://es2:9200``) or through a
``.env`` file in the working directory.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PYATLAS_", env_file=".env", extra="ignore")

    # --- Elasticsearch -------------------------------------------------------
    es_hosts: str = "http://localhost:9200"
    es_username: Optional[str] = None
    es_password: Optional[str] = None
    es_api_key: Optional[str] = None
    es_ca_certs: Optional[str] = None
    es_verify_certs: bool = True
    es_index_prefix: str = "atlas"
    es_shards: int = 1
    es_replicas: int = 0
    # "wait_for" gives read-your-writes semantics for search (like Atlas);
    # "false" is faster for bulk loads.
    es_refresh: str = "wait_for"
    # Development only: keep everything in process memory instead of Elasticsearch.
    in_memory: bool = False

    # --- Type system ---------------------------------------------------------
    models_dir: Path = PROJECT_ROOT / "models"
    load_models: bool = True
    # Reload the in-memory type registry if another node changed typedefs.
    typedef_cache_check_secs: float = 5.0

    # --- Server / UI ---------------------------------------------------------
    ui_dir: Path = PROJECT_ROOT / "ui"
    # "v1" = classic Backbone UI (served at /index.html), "v3" = React UI (served at /n3/index.html)
    default_ui: str = "v1"
    server_name: str = "pyatlas"
    version: str = "2.4.0-pyatlas-0.1.0"

    # --- Authentication ------------------------------------------------------
    auth_enabled: bool = True
    # Atlas-compatible file: user=ROLE::sha256(password)
    users_file: Path = PROJECT_ROOT / "conf" / "users-credentials.properties"
    # key that signs the session cookie; MUST be set (same value on all nodes) in production.  When unset a
    # random key is generated at start-up (sessions end with a restart and do not work across nodes).
    session_secret: Optional[str] = None
    # UI idle timeout reported to the UI (Atlas atlas.session.timeout.secs); -1 = none
    session_timeout_secs: int = -1
    # absolute lifetime of a login session (the signed cookie is rejected afterwards)
    session_max_age_secs: int = 8 * 3600
    # mark the session cookie "Secure" (only sent over HTTPS) - enable when served via HTTPS
    session_cookie_secure: bool = False
    # Atlas' CSRF filter: data-changing API calls from browsers need the X-XSRF-HEADER session token
    csrf_enabled: bool = True
    csrf_browser_useragents: str = "^Mozilla.*,^Opera.*,^Chrome.*"
    # failed logins per user name and client address before a temporary lock-out
    login_max_failures: int = 5
    login_lockout_secs: int = 300
    # security response headers (as Atlas' HeadersUtil); HSTS only when served via HTTPS
    security_headers: bool = True
    hsts: bool = False

    # OpenID Connect (Keycloak) bearer tokens, used by the Aurelius frontend; see pyatlas/oidc.py
    oidc_enabled: bool = False
    # accepted "iss" values, comma separated (the URL the browser uses, e.g. https://host/aurelius/auth/realms/m4i)
    oidc_issuers: str = ""
    # where pyatlas fetches the signing keys (default: <first issuer>/protocol/openid-connect/certs); set it when
    # pyatlas reaches Keycloak under another name, e.g. http://keycloak:8080/aurelius/auth/realms/m4i/protocol/...
    oidc_jwks_url: Optional[str] = None
    # accepted clients (azp or aud), comma separated; empty = any client of the realm (as Atlas' Keycloak adapter)
    oidc_clients: str = ""
    oidc_username_claim: str = "preferred_username"
    # clients whose client roles are added to the realm roles as groups (comma separated)
    oidc_client_roles: str = ""
    oidc_leeway_secs: int = 30
    # Keycloak users can also log in to pyatlas' own login form (Atlas UIs) with user name + password; needs a
    # client with "Direct access grants" (the token URL defaults to the JWKS URL's .../token)
    oidc_password_login: bool = False
    oidc_token_url: Optional[str] = None
    oidc_password_client: str = "m4i_atlas"
    oidc_password_client_secret: Optional[str] = None

    # --- Authorization -------------------------------------------------------
    # "simple" = Atlas' AtlasSimpleAuthorizer (JSON policy file), "none" = allow everything
    authorizer: str = "simple"
    authz_policy_file: Path = PROJECT_ROOT / "conf" / "atlas-simple-authz-policy.json"

    # POST /admin/importfile only reads ZIP files below this directory
    import_dir: Path = PROJECT_ROOT / "data" / "import"
    # maximum size of a request body (uploads such as import ZIPs, CSV/XLSX files) in MB
    max_upload_mb: int = 512
    # maximum total uncompressed size of an import ZIP in MB (zip-bomb protection)
    max_import_uncompressed_mb: int = 4096

    # directory for generated search-result / glossary export files and uploaded imports
    download_dir: Path = PROJECT_ROOT / "data" / "downloads"

    # metrics history (GET /admin/metricsstats): snapshot interval and retention
    metrics_persist_interval_secs: int = 3600
    metrics_ttl_hours: int = 336
    # defaults for POST /admin/audits/ageout?useAuditConfig=true (0 = disabled)
    audit_ageout_ttl_days: int = 0
    audit_ageout_count: int = 0

    # Atlas export ZIPs imported at start-up (comma separated paths); each file is imported only once
    # per index prefix (tracked by its SHA-256 in the meta index)
    import_on_start: str = ""
    # "once" = skip files that were imported before (by SHA-256), "always" = import on every start
    # (entities from the ZIP are reset to its content; other data is kept)
    import_on_start_mode: str = "once"

    # --- Aurelius (pyatlas/aurelius) -------------------------------------------
    # search documents + App Search compatible search for the Aurelius frontend
    aurelius_enabled: bool = True
    # quality result documents loaded into empty quality indices at start-up (comma separated JSON files, e.g.
    # the sample atlas-dev-quality.json / atlas-dev-gov-quality.json of backend/m4i-atlas-post-install/data)
    aurelius_quality_seed: str = ""
    # seconds without entity writes before the search documents are rebuilt (at the latest after max delay)
    aurelius_rebuild_debounce_secs: float = 1.0
    aurelius_rebuild_max_delay_secs: float = 10.0

    # --- Behaviour -----------------------------------------------------------
    search_max_limit: int = 10000
    search_default_limit: int = 100
    create_shell_entity_for_missing_ref: bool = False
    max_relationships_per_entity: int = 50000
    lineage_max_depth: int = 50
    lineage_on_demand_enabled: bool = False
    lineage_on_demand_default_node_count: int = 3
    # maximum number of entities materialised for DSL joins / navigation / aggregation
    dsl_max_join: int = 100000

    @property
    def es_host_list(self) -> List[str]:
        return [h.strip() for h in self.es_hosts.split(",") if h.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
