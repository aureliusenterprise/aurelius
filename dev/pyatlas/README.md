# Aurelius on pyatlas - local stack

Reverse proxy with the Angular frontend (`apps/atlas`), Keycloak, pyatlas and Elasticsearch. It replaces
`dev/docker-compose.yaml` (Apache Atlas, Kafka, Enterprise Search) for the pyatlas migration.

```bash
dev/pyatlas/init-env.sh && docker compose -f dev/pyatlas/docker-compose.yml up --build -d   # Windows: dev\pyatlas\start.bat
```

The first start writes `dev/pyatlas/.env` with random secrets (Keycloak admin password, pyatlas session secret,
reverse proxy client secret and cookie passphrase); compose does not start without them. Keep `.env` private.

| What | URL | Login |
| --- | --- | --- |
| Aurelius Atlas frontend | http://localhost:9090/aurelius/atlas/ | `atlas` (admin + steward), `steward`, `scientist`; password = user name |
| Keycloak admin console | http://localhost:9090/aurelius/auth/admin/ | `admin` / `KEYCLOAK_ADMIN_PASSWORD` from `.env` |
| pyatlas (Atlas UIs, `api/docs`) | http://localhost:9090/aurelius/atlas2/ | the same Keycloak users |
| Elasticsearch 9.5 | http://localhost:9200 (this machine only) | - |
| Kibana | http://localhost:9090/aurelius/kibana/ | Keycloak users with the realm role `ROLE_ADMIN` (`atlas`); data views for the Atlas and Aurelius indices are created at start |

The first start builds three images (the frontend build runs `npm ci` + `nx build atlas`, several minutes),
imports the Aurelius sample data into pyatlas and the realm `m4i` into Keycloak. Passwords of the three demo users
can be set on the first start with `AURELIUS_ATLAS_PASSWORD`, `AURELIUS_STEWARD_PASSWORD`,
`AURELIUS_SCIENTIST_PASSWORD`; later changes go through the Keycloak console.

## How the pieces fit

- The browser only talks to the reverse proxy (`reverse-proxy/aurelius.conf`): `/aurelius/atlas/` is the
  frontend, `/aurelius/atlas/atlas/` the Atlas v2 API of pyatlas, `/aurelius/auth/` Keycloak.
- The frontend logs in with Keycloak (realm `m4i`, client `m4i_atlas`) and sends the access token to pyatlas.
  pyatlas validates it (`PYATLAS_OIDC_*`, `backend/pyatlas/pyatlas/oidc.py`) and maps the realm roles
  `ROLE_ADMIN`, `DATA_STEWARD`, `DATA_SCIENTIST` onto the groups of its authorization policy.
- `AURELIUS_PUBLIC_URL` (default `http://localhost:9090`) must be the URL the browser uses: it is the token
  issuer pyatlas accepts and the redirect URL Keycloak allows.

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
  http://localhost:9090/aurelius/atlas2/api/aurelius/quality/results \
  -d '{"results": [{"quality": "nl1--nl1hr--nl1hr001--func_organization--28", "dqscore": 0.95}]}'
```

Deployment pipelines register technical lineage (processes, Kubernetes objects, Kafka topics, Elastic indices,
Kibana objects) with the lineage registration API, which pyatlas now serves with the paths and payloads of the
old m4i-lineage-rest-api under `/aurelius/lin_api/` (e.g. `POST /aurelius/lin_api/process/generic_process/`,
Keycloak token or Keycloak user with write access, e.g. `steward`; Swagger: http://localhost:9090/aurelius/atlas2/api/docs):

```
curl -u atlas:atlas -H "Content-Type: application/json" -X POST \
  http://localhost:9090/aurelius/lin_api/kubernetes/kubernetes_environment/ \
  -d '{"qualifiedName": "prod", "name": "Production", "kubernetesClusters": []}'
```

The governance dashboard figures are served at `/aurelius/atlas/api/data_governance_dashboard` (the dashboard
page in `apps/atlas` exists but is not linked in the frontend's routes).

Kibana runs behind the reverse proxy: the proxy asks for a Keycloak login (mod_auth_openidc, confidential client
`aurelius_proxy`, created by the `keycloak-init` job) and lets only users with the realm role `ROLE_ADMIN` through.
Set `AURELIUS_PROXY_CLIENT_SECRET` and `AURELIUS_PROXY_CRYPTO_PASSPHRASE` for anything but a local test.

The Kibana dashboard **Aurelius activity** (http://localhost:9090/aurelius/kibana/app/dashboards#/view/aurelius-activity)
shows logins and changes per day: logins per day and active users (pyatlas access log `atlas_access`: one entry
per Keycloak session, Atlas UI form login, or Basic-auth user and day), changes per day by kind and by user, and
who changed which entity types (entity audits `atlas_audit`, now with the entity's type and name). Discover has
the underlying events in the data views "Logins (pyatlas access log)" and "Atlas entity audits".

The dashboard **Aurelius usage** (`.../app/dashboards#/view/aurelius-usage`) shows how the frontend is used and how
people move through it, from the frontend's clickstream (every page a logged-in user opens, `atlas_clickstream`):
page views and visits per day, the most used pages, where people go next, where visits start, time on page,
search texts, the most viewed entities and entity types, and usage per user. A visit is a run of page views of
one user without a pause of 30 minutes.

Elasticsearch is 9.5 (Enterprise Search / App Search does not exist in 9; pyatlas answers the frontend's App Search
queries itself). Its data lives in the volume `esdata9`: stacks started before the switch from 8.15 begin with a
fresh Elasticsearch and re-import the sample data. The old 8.15 volume can be removed with
`docker volume rm aurelius-pyatlas_esdata`.

If you started an earlier version of this stack, the sample data is already imported; the search indices are
created and filled at the next start. Status: http://localhost:9090/aurelius/atlas2/api/aurelius/admin/search/status

## Security settings of this stack

What the stack does (hardening round of 29 Sep 2026) and what is left for production (phase 6):

| Topic | This stack | Before production |
| --- | --- | --- |
| Secrets | random, generated into `.env`; compose refuses to start without them; a Keycloak started with the old default admin password gets the new one (`keycloak-init`) | from a secret store |
| Users | only Keycloak users (`PYATLAS_FILE_USERS_ENABLED=false`; the image's `admin`/`admin` file user is off); a Keycloak user named like a file user gets only its token's roles; tokens only of client `m4i_atlas` (`PYATLAS_OIDC_CLIENTS`) | remove or change the demo users (password = user name) |
| Keycloak | brute force protection (10 failures), password policy for new passwords (8 characters, not the user name), SSL required for external addresses; metrics and health not reachable through the proxy | production mode (`start`) with a database and TLS, Keycloak 26, admin console only from admin networks |
| Elasticsearch | port 9200 bound to this machine only | security with TLS and a pyatlas API key |
| Access | Aurelius search, dashboard and lineage listing need an Aurelius role (entity-read); index status for admins | |
| Limits | JSON bodies 32 MB, uploads 512 MB (pyatlas and proxy), 120 page views per user and minute; Keycloak password checks off the request loop and cached 60 s for scripts | |
| Personal data | logins and page views are deleted after 180 days (`PYATLAS_ACCESS_LOG_RETENTION_DAYS`, `PYATLAS_CLICKSTREAM_RETENTION_DAYS`) | agree the period with the privacy officer |
| Proxy | security headers on every answer (nosniff, frame options, referrer and permissions policy, HSTS over HTTPS), no server version, no TRACE; client address for lock-out and access log only from the proxy's `X-Forwarded-For` | TLS; `PYATLAS_SESSION_COOKIE_SECURE=true`, `PYATLAS_HSTS=true` |
| Containers | restart unless stopped, log rotation (10 MB x 5), health checks, pyatlas runs as a non-root user | pinned image digests, resource limits |
