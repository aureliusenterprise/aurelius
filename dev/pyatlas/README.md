# Aurelius on pyatlas - local stack (several tenants)

Reverse proxy with the Angular frontend (`apps/atlas`), Keycloak, pyatlas, Elasticsearch, Kibana and a log shipper.
One set of containers serves several tenants (organisations); each has its own Keycloak realm, its own URLs, its
own indices and API keys, its own Kibana space and its own log data streams.

```bash
dev/pyatlas/init-env.sh && docker compose -f dev/pyatlas/docker-compose.yml up --build -d   # Windows: dev\pyatlas\start.bat
```

`init-env` writes `dev/pyatlas/.env` with random secrets and adds new ones to an existing `.env` (this version adds
`ELASTIC_PASSWORD`, `KIBANA_SYSTEM_PASSWORD`, `KIBANA_ENCRYPTION_KEY`, `PYATLAS_ES_PASSWORD`, `FILEBEAT_PASSWORD`,
`AURELIUS_OPERATOR_PASSWORD`); compose does not start without them. Keep `.env` private.

The first start creates the platform and the tenant `m4i` (job `aurelius-init`, repeated harmlessly at every
start). `m4i` is the former single-tenant installation: realm `m4i` with its users, the sample data, and - once -
a copy of an existing installation's indices `atlas_*` to `aurelius_m4i_*`. It is also our own tenant for tests.

| What | URL | Login |
| --- | --- | --- |
| Frontend of tenant m4i | http://localhost:9090/aurelius/m4i/atlas/ (the old http://localhost:9090/aurelius/atlas/ redirects) | `atlas` (admin + steward), `steward`, `scientist`; password = user name |
| Kibana of tenant m4i | http://localhost:9090/aurelius/m4i/kibana/ | users of realm `m4i` with `ROLE_ADMIN` (`atlas`) |
| pyatlas of tenant m4i (Atlas UIs, `api/docs`) | http://localhost:9090/aurelius/m4i/atlas2/ | the same users |
| Lineage API of tenant m4i | http://localhost:9090/aurelius/m4i/lin_api/ (the old `/aurelius/lin_api/` still works for m4i) | Keycloak user or token of realm `m4i` |
| Kibana for operators (all tenants) | http://localhost:9090/aurelius/platform/kibana/ | realm `platform`: `operator` / `AURELIUS_OPERATOR_PASSWORD` from `.env` |
| Keycloak admin console | http://localhost:9090/aurelius/auth/admin/ | `admin` / `KEYCLOAK_ADMIN_PASSWORD` from `.env` |
| Elasticsearch 9.5 | http://localhost:9200 (this machine only) | `elastic` / `ELASTIC_PASSWORD` from `.env` |

## Tenants

```bash
C="docker compose -f dev/pyatlas/docker-compose.yml run --rm aurelius-admin"
$C tenant create acme --name "ACME" --admin-user anna --admin-email anna@acme.example   # prints anna's temporary password
$C tenant create acme --sample-data /aurelius-data/sample_data.zip                      # optional demo content
$C tenant list
$C tenant entra acme --directory-id <Entra tenant id> --client-id <app id> --client-secret <secret> [--only-entra]
$C tenant suspend acme        # resume acme
$C tenant export acme --out /tenants/acme.zip
$C tenant delete acme --yes
```

A new tenant needs no restart and no proxy change: `http://localhost:9090/aurelius/acme/atlas/` works at once.
`tenant create` is idempotent (running it again repairs clients, keys, space and dashboards and keeps the data).

**Entra ID of a customer.** The customer registers an app in Entra ID with the redirect URI
`<public URL>/aurelius/auth/realms/<tenant>/broker/entra/endpoint`, defines app roles `ROLE_ADMIN`, `DATA_STEWARD`,
`DATA_SCIENTIST` (or others, mapped with `--map AppRole=ROLE_ADMIN`) and gives us the directory id, client id and a
secret; `tenant entra` adds the identity provider and the role mappers to the tenant's realm. With `--only-entra`
the login page goes straight to Entra ID.

## How the pieces fit

- The browser only talks to the reverse proxy (`docker/aurelius-reverse-proxy/aurelius.conf`). The tenant comes from the URL path
  `/aurelius/<tenant>/...` only: the proxy removes any `X-Aurelius-Tenant` header of the client and sets its own;
  pyatlas believes it only from the proxy (`PYATLAS_TRUSTED_PROXIES`).
- The frontend is one build for all tenants: it takes its base path from the URL and its realm from
  `/aurelius/<tenant>/atlas/config.json` (answered by pyatlas).
- pyatlas (`backend/pyatlas/pyatlas/tenancy.py`) runs a tenant context per tenant - its own store (`aurelius_<tenant>_*`,
  with the tenant's Elasticsearch API key), types, search documents, jobs, downloads - started on first use and
  stopped when idle. A token is accepted only if it was issued by the realm of the tenant in the URL; UI sessions
  have a cookie per tenant.
- Kibana: one Kibana, a space per tenant. The proxy logs the user in at the tenant's realm (mod_auth_openidc,
  `docker/aurelius-reverse-proxy/kibana-tenants.conf`), requires `ROLE_ADMIN` and forwards the request with the tenant's Kibana API
  key (read access to the tenant's indices and log data streams, its space only). Opening another tenant's space
  ends the login and asks for a login at that tenant.
- Logs: pyatlas (JSON, with tenant), the proxy (JSON, with tenant) and Keycloak (JSON, login events with the realm)
  are read by Filebeat; the Elasticsearch pipeline `aurelius-logs` checks the tenant against the registry and routes
  each line to `logs-aurelius.<pyatlas|proxy|keycloak>-<tenant>` (unknown or none: `-platform`, operators only).
- `aurelius-admin` (`backend/pyatlas/pyatlas/tenant_admin.py`) creates and removes tenants in all of these places.
- `AURELIUS_PUBLIC_URL` (default `http://localhost:9090`) must be the URL the browser uses: it is part of the token
  issuers pyatlas accepts and of the redirect URLs Keycloak allows.

## Status

Login, roles, browsing, search with filters and facets, entity details, editing with the live governance
quality check, and lineage work. pyatlas computes from the metadata (`backend/pyatlas/pyatlas/aurelius`), about
a second after every change:

- the search documents (replacing the synchronize-app-search Flink job),
- governance quality: the m4i-governance-data-quality rules per entity (replacing the update-gov-data-quality
  Flink job); the editor's `validate_entity` check runs the same rules on the unsaved entity,
- the data quality roll-up field -> data attribute -> breadcrumb (replacing `propagate_quality.py`),
- the lineage model of processes and datasets (replacing m4i-lineage-model and data2model).

Rules are evaluated by a parser that only allows the quality functions, never `eval`. Data quality results
start with the sample results (`PYATLAS_AURELIUS_QUALITY_SEED`); quality tooling posts new scores as a Keycloak user with `ROLE_ADMIN`:

```
curl -u atlas:atlas -H "Content-Type: application/json" -X POST \
  http://localhost:9090/aurelius/m4i/atlas2/api/aurelius/quality/results \
  -d '{"results": [{"quality": "nl1--nl1hr--nl1hr001--func_organization--28", "dqscore": 0.95}]}'
```

Deployment pipelines register technical lineage (processes, Kubernetes objects, Kafka topics, Elastic indices,
Kibana objects) with the lineage registration API, which pyatlas now serves with the paths and payloads of the
old m4i-lineage-rest-api under `/aurelius/<tenant>/lin_api/` (e.g. `POST /aurelius/lin_api/process/generic_process/`,
Keycloak token or Keycloak user with write access, e.g. `steward`; Swagger: http://localhost:9090/aurelius/m4i/atlas2/api/docs):

```
curl -u atlas:atlas -H "Content-Type: application/json" -X POST \
  http://localhost:9090/aurelius/m4i/lin_api/kubernetes/kubernetes_environment/ \
  -d '{"qualifiedName": "prod", "name": "Production", "kubernetesClusters": []}'
```

The governance dashboard figures are served at `/aurelius/<tenant>/atlas/api/data_governance_dashboard` (the dashboard
page in `apps/atlas` exists but is not linked in the frontend's routes).

Kibana runs behind the reverse proxy: the proxy asks for a login at the tenant's realm (mod_auth_openidc,
confidential client `aurelius_proxy` of every realm, created by `aurelius-admin`) and lets only users with the realm
role `ROLE_ADMIN` through. `AURELIUS_PROXY_CLIENT_SECRET` of earlier versions is no longer used (every realm has its
own generated secret).

Every tenant's Kibana space has three dashboards (operators see them over all tenants in the space `platform`).

The Kibana dashboard **Aurelius activity** (`.../aurelius/<tenant>/kibana/` -> Dashboards)
shows logins and changes per day: logins per day and active users (access log `aurelius_<tenant>_access`: one entry
per Keycloak session, Atlas UI form login, or Basic-auth user and day), changes per day by kind and by user, and
who changed which entity types (entity audits `aurelius_<tenant>_audit`, with the entity's type and name), and from
the tenant's Keycloak login events: logins and failed logins per day, failed logins by user and reason, and logins
through the organisation's identity provider (e.g. Entra ID) versus local accounts.

The dashboard **Aurelius health** shows API requests per day and status, errors and warnings, the slowest API
calls, lineage API calls per endpoint, quality result uploads, and all requests of the tenant's addresses at the
proxy (from the log data streams `logs-aurelius.*-<tenant>`).

The dashboard **Aurelius usage** shows how the frontend is used and how
people move through it, from the frontend's clickstream (every page a logged-in user opens, `aurelius_<tenant>_clickstream`):
page views and visits per day, the most used pages, where people go next, where visits start, time on page,
search texts, the most viewed entities and entity types, and usage per user. A visit is a run of page views of
one user without a pause of 30 minutes.

Elasticsearch is 9.5 (Enterprise Search / App Search does not exist in 9; pyatlas answers the frontend's App Search
queries itself). Its data lives in the volume `esdata9`: stacks started before the switch from 8.15 begin with a
fresh Elasticsearch and re-import the sample data. The old 8.15 volume can be removed with
`docker volume rm aurelius-pyatlas_esdata`.

If you started an earlier version of this stack, the sample data is already imported; the search indices are
created and filled at the next start. Status: http://localhost:9090/aurelius/m4i/atlas2/api/aurelius/admin/search/status

## Security settings of this stack

What the stack does (hardening round of 29 Sep 2026) and what is left for production (phase 6):

| Topic | This stack | Before production |
| --- | --- | --- |
| Secrets | random, generated into `.env`; compose refuses to start without them; a Keycloak started with the old default admin password gets the new one (`keycloak-init`) | from a secret store |
| Users | only Keycloak users (`PYATLAS_FILE_USERS_ENABLED=false`; the image's `admin`/`admin` file user is off); a Keycloak user named like a file user gets only its token's roles; tokens only of client `m4i_atlas` (`PYATLAS_OIDC_CLIENTS`) | remove or change the demo users (password = user name) |
| Keycloak | brute force protection (10 failures), password policy for new passwords (8 characters, not the user name), SSL required for external addresses; metrics and health not reachable through the proxy | production mode (`start`) with a database and TLS, Keycloak 26, admin console only from admin networks |
| Elasticsearch | security on; pyatlas' own user reads only the tenant registry, every tenant context has an API key limited to `aurelius_<tenant>_*`, Kibana keys per tenant; port 9200 bound to this machine only | TLS |
| Access | Aurelius search, dashboard and lineage listing need an Aurelius role (entity-read); index status for admins | |
| Limits | JSON bodies 32 MB, uploads 512 MB (pyatlas and proxy), 120 page views per user and minute; Keycloak password checks off the request loop and cached 60 s for scripts | |
| Personal data | logins and page views are deleted after 180 days (`PYATLAS_ACCESS_LOG_RETENTION_DAYS`, `PYATLAS_CLICKSTREAM_RETENTION_DAYS`) | agree the period with the privacy officer |
| Proxy | security headers on every answer (nosniff, frame options, referrer and permissions policy, HSTS over HTTPS), no server version, no TRACE; client address for lock-out and access log only from the proxy's `X-Forwarded-For` | TLS; `PYATLAS_SESSION_COOKIE_SECURE=true`, `PYATLAS_HSTS=true` |
| Containers | restart unless stopped, log rotation (10 MB x 5), health checks, pyatlas runs as a non-root user | pinned image digests, resource limits |
