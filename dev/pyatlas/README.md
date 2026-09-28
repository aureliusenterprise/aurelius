# Aurelius on pyatlas - local stack

Reverse proxy with the Angular frontend (`apps/atlas`), Keycloak, pyatlas and Elasticsearch. It replaces
`dev/docker-compose.yaml` (Apache Atlas, Kafka, Enterprise Search) for the pyatlas migration.

```bash
docker compose -f dev/pyatlas/docker-compose.yml up --build -d      # Windows: dev\pyatlas\start.bat
```

| What | URL | Login |
| --- | --- | --- |
| Aurelius Atlas frontend | http://localhost:9090/aurelius/atlas/ | `atlas` (admin + steward), `steward`, `scientist`; password = user name |
| Keycloak admin console | http://localhost:9090/aurelius/auth/admin/ | `admin` / `admin` (`KEYCLOAK_ADMIN_PASSWORD`) |
| pyatlas (Atlas UIs, `api/docs`) | http://localhost:9090/aurelius/atlas2/ | the same Keycloak users, or pyatlas' own `admin` / `admin` |
| Elasticsearch | http://localhost:9200 | - |
| Kibana | http://localhost:5601 | - (data views for the Atlas and Aurelius indices are created at start) |

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

Login, roles, browsing, search with filters and facets, entity details with governance quality, and editing
work. The search documents are computed by pyatlas from the metadata (`backend/pyatlas/pyatlas/aurelius`) and
follow every change about a second later. Data quality and governance quality results are the sample results
of the Aurelius post-install job (`PYATLAS_AURELIUS_QUALITY_SEED`); computing governance quality in pyatlas is
phase 3. Lineage model, dashboard and `validate_entity` follow in phases 3-4.

If you started an earlier version of this stack, the sample data is already imported; the search indices are
created and filled at the next start. Status: http://localhost:9090/aurelius/atlas2/api/aurelius/admin/search/status
