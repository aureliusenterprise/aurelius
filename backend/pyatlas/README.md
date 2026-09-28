# pyatlas

A Python re-implementation of the [Apache Atlas](https://atlas.apache.org/) metadata server.
It keeps Atlas' REST API (`/api/atlas/v2/...`) and web UI, but replaces Atlas' storage stack
(JanusGraph + HBase + Solr + ZooKeeper) with **Elasticsearch alone**. Elasticsearch stores the
metadata and also serves as the full-text index.

Existing Atlas clients (the `apache-atlas` Python client, `curl` scripts and REST-based
integrations) should work unchanged against it. Both Atlas web UIs are bundled and served by the
Python server:

* the classic UI at `/index.html`
* the React UI at `/n3/index.html`

### In the Aurelius monorepo

pyatlas lives in `backend/pyatlas` of the Aurelius monorepo and replaces Apache Atlas, Kafka and the Flink jobs
(see `docs/migration/`). It keeps its own Python 3.12 environment (the workspace Poetry environment is Python
3.8); the Nx targets run it in Docker: `nx run pyatlas:test`, `nx run pyatlas:serve`. Docker builds use the
repository root as context (`docker build -f backend/pyatlas/Dockerfile .`), like the other Aurelius images.

* The Aurelius (m4i) type definitions are bundled as `models/9000-Aurelius/*.json`, generated from
  `libs/m4i-atlas-core` by `scripts/gen_m4i_models.py`.
* `parity/` holds the migration checks (`python -m parity --help`, on Windows `run_parity.bat`): stored data,
  search/quality indices, same-changes-same-results, recorded API responses and the quality-rule grammar;
  the browser journeys are in `apps/atlas-e2e`.
* Keycloak (OIDC) access tokens are accepted next to the file users when `PYATLAS_OIDC_ENABLED=true`
  (`PYATLAS_OIDC_ISSUERS`, `PYATLAS_OIDC_JWKS_URL`, `PYATLAS_OIDC_CLIENTS`, `PYATLAS_OIDC_CLIENT_ROLES`); the realm
  roles become the groups of the authorization policy. `dev/pyatlas` runs the whole Aurelius stack on pyatlas.
* `docker-compose.parity.yml` runs pyatlas with the Aurelius sample data next to an old stack
  (ports 21100 / 9201 / 5602).

## Status: full Atlas v2 REST API + admin API

All 158 routes of Atlas' `v2` REST resources (`TypesREST`, `EntityREST`, `RelationshipREST`,
`DiscoveryREST`, `LineageREST`, `GlossaryREST`, `IndexRecoveryREST`) and of `AdminResource` are
implemented. The deprecated v1 API (`/api/atlas/entities`, `/api/atlas/types`, ...) is not.

| Area | Status |
|---|---|
| Type system: `types/typedefs` CRUD, headers, per-category lookups, validation, model files + patches in `models/` | ✅ |
| Entities: create/update (bulk, partial, by unique attribute), get (with ext-info), headers, delete (soft, cascading over compositions), purge | ✅ |
| Relationships: relationship attributes, legacy reference attributes, `v2/relationship` CRUD | ✅ |
| Classifications: add/update/delete/bulk/set, **propagation** along relationships (incl. lineage), blocked propagation | ✅ |
| Labels, custom attributes, business metadata (incl. CSV/XLSX bulk import) | ✅ |
| Entity audits (`entity/{guid}/audit`) | ✅ |
| Search: basic, quick, suggestions, full-text, attribute, relationship search (with filters), saved searches, CSV result downloads | ✅ |
| DSL search: `from/where/isa/has`, joins and path navigation, `select`, `groupby`, `count/min/max/sum`, `orderby`, `limit/offset` | ✅ |
| Lineage: classic and on-demand (`POST v2/lineage/{guid}`), by unique attribute | ✅ |
| Glossary: glossaries, terms, categories, term assignments, related terms, CSV/XLSX term import and template | ✅ |
| Admin: export / import (Atlas ZIP format, sync + async), import from server file, admin audits (details/summary/batches/ageout), metrics + metrics history & charts, patches, checkstate, tasks, active searches, debug metrics, thread dump, index recovery | ✅ |
| Authentication: file based (`conf/users-credentials.properties`), UI form login + HTTP Basic | ✅ |
| Authorization: Atlas simple authorizer (roles from a JSON policy file) on every REST call, search-result scrubbing, UI edit flags | ✅ |
| LDAP / Kerberos / OpenID Connect (Keycloak) | ⏳ future (plug into `pyatlas/auth.py` `Authenticator`) |
| Kafka hooks / notifications, Ranger authorisation | not planned yet |

> **Validation note:** the automated test suite (`tests/`) runs the full server against an
> in-memory emulation of the Elasticsearch API (`pyatlas/store/memory.py`). Both bundled UIs
> have been checked in a browser against that emulation. The first runs against a real
> Elasticsearch 8 cluster (see `docker-compose.yml`) should still be treated as integration
> testing.

## Quick start

### Docker Compose (Elasticsearch + pyatlas)

```bash
docker compose up --build
# UI:   http://localhost:21000   (admin / admin)
# API:  http://localhost:21000/api/atlas/v2/types/typedefs/headers
# Docs: http://localhost:21000/api/docs
# Kibana: http://localhost:5601    (Discover: data views "Atlas entities", "Atlas relationships", ... are
#         created at start-up by the kibana-setup job; Dev Tools: GET atlas_entities/_search)
python scripts/load_sample_data.py      # optional demo data
```

`PYATLAS_IMPORT_ON_START` (or `--import-zip <file>`) imports Atlas export ZIPs when the server starts, for
example `sample_data.zip` from the project folder. By default each file is imported only once: its SHA-256
is recorded in the meta index. With `PYATLAS_IMPORT_ON_START_MODE=always` it is imported on every start,
which resets the entities from the ZIP to its content and keeps other data. `docker-compose.yml` uses
`always`. On Windows, `run_pyatlas.bat` builds the image and runs it against an Elasticsearch that
is already running on the machine (`host.docker.internal:9200`).

### Local Python against your own Elasticsearch

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
set PYATLAS_ES_HOSTS=http://localhost:9200         # or export on Linux/macOS
python -m pyatlas --port 21000
```

### Without Elasticsearch (demo / development)

```bash
python -m pyatlas --in-memory
python -m pyatlas --in-memory --import-zip sample_data.zip    # start with an Atlas export
```

To import into a running server: `python scripts/import_zip.py sample_data.zip --url http://localhost:21000`,
or `POST /api/atlas/admin/import`.

This mode keeps everything in process memory and loses it on restart. Its query engine only
approximates Elasticsearch.

### Tests

```bash
pip install -e ".[dev]"
pytest                                               # in-memory Elasticsearch stand-in
PYATLAS_TEST_ES_HOSTS=http://localhost:9200 pytest   # the same tests against a real cluster
```

Against a real cluster every test uses its own `pytest_<random>_*` indices and deletes them afterwards
(optional: `PYATLAS_TEST_ES_USERNAME`, `PYATLAS_TEST_ES_PASSWORD`, `PYATLAS_TEST_ES_VERIFY_CERTS=false`).
On Windows without Python, `run_tests.bat` runs both variants in a `python:3.12-slim` Docker container
against `http://host.docker.internal:9200` and writes `run_tests.log`.

## Configuration

All settings are environment variables with the `PYATLAS_` prefix, or entries in a `.env` file
(see `pyatlas/config.py`):

| Variable | Default | Meaning |
|---|---|---|
| `PYATLAS_ES_HOSTS` | `http://localhost:9200` | comma-separated Elasticsearch URLs |
| `PYATLAS_ES_USERNAME` / `PYATLAS_ES_PASSWORD` / `PYATLAS_ES_API_KEY` | – | Elasticsearch credentials |
| `PYATLAS_ES_CA_CERTS`, `PYATLAS_ES_VERIFY_CERTS` | – / `true` | TLS |
| `PYATLAS_ES_INDEX_PREFIX` | `atlas` | index name prefix (lower case) |
| `PYATLAS_ES_SHARDS`, `PYATLAS_ES_REPLICAS` | `1`, `0` | settings for newly created indices |
| `PYATLAS_ES_REFRESH` | `wait_for` | refresh policy of writes (`wait_for` = read-your-writes in search, `false` = faster bulk loads) |
| `PYATLAS_MODELS_DIR`, `PYATLAS_LOAD_MODELS` | `models/`, `true` | Atlas model files loaded (and patched) at start-up |
| `PYATLAS_AUTH_ENABLED` | `true` | turn authentication off for local experiments |
| `PYATLAS_USERS_FILE` | `conf/users-credentials.properties` | `user=GROUPS::hash`, hash = BCrypt (`scripts/hash_password.py`), `sha256(password{user})` or `sha256(password)` |
| `PYATLAS_SESSION_SECRET` | *(random per start)* | key signing the UI session cookie. **Set it** (same on all nodes); unset = random, sessions end on restart |
| `PYATLAS_SESSION_TIMEOUT_SECS` | `-1` | UI idle timeout |
| `PYATLAS_SESSION_MAX_AGE_SECS` | `28800` | absolute lifetime of a login session |
| `PYATLAS_SESSION_COOKIE_SECURE`, `PYATLAS_HSTS` | `false` | set to `true` when pyatlas is served via HTTPS |
| `PYATLAS_CSRF_ENABLED` | `true` | Atlas' CSRF protection for browser clients (header `X-XSRF-HEADER`) |
| `PYATLAS_LOGIN_MAX_FAILURES`, `PYATLAS_LOGIN_LOCKOUT_SECS` | `5`, `300` | lock-out after failed logins (per user name and client address) |
| `PYATLAS_IMPORT_DIR` | `data/import` | `POST /admin/importfile` only reads files below this directory |
| `PYATLAS_MAX_UPLOAD_MB`, `PYATLAS_MAX_IMPORT_UNCOMPRESSED_MB` | `512`, `4096` | request body limit; uncompressed size limit of import ZIPs |
| `PYATLAS_AUTHORIZER` | `simple` | `simple` = Atlas simple authorizer, `none` = everybody may do everything |
| `PYATLAS_AUTHZ_POLICY_FILE` | `conf/atlas-simple-authz-policy.json` | roles, user → role and group → role mappings |
| `PYATLAS_DEFAULT_UI` | `v1` | UI opened after login: `v1` = classic UI, `v3` = React UI |
| `PYATLAS_SEARCH_MAX_LIMIT` | `10000` | maximum page size for searches |
| `PYATLAS_CREATE_SHELL_ENTITY_FOR_MISSING_REF` | `false` | create shell (incomplete) entities for unresolved references instead of failing |
| `PYATLAS_IN_MEMORY` | `false` | same as `--in-memory` |
| `PYATLAS_IMPORT_ON_START` | – | comma-separated Atlas export ZIPs imported at start-up (same as `--import-zip`) |
| `PYATLAS_IMPORT_ON_START_MODE` | `once` | `once` = skip files imported before, `always` = import at every start |

## Export / import

`POST /api/atlas/admin/export` writes, and `POST /admin/import`, `/admin/importfile` and
`/admin/async/import` read, Atlas' own ZIP layout (`atlas-export-info.json`, `atlas-typesdef.json`,
`atlas-export-order.json`, `<guid>.json`). Archives therefore move between Apache Atlas and pyatlas in
both directions.

| Option | Where | Meaning |
|---|---|---|
| `fetchType` | export | `full` (default), `connected`, `incremental` |
| `changeMarker` | export | with `incremental`, only entities updated at or after this time. Use the `changeMarker` of the previous export's result. A hive_table start entity is fetched `connected`. |
| `matchType` | export | `startsWith`, `endsWith`, `contains`, `matches`, `forType` for the unique attributes of `itemsToExport` |
| `skipLineage` | export | do not follow processes |
| `replicatedTo` / `replicatedFrom` | export / import | name of the other server (`<dc>$<server>`). Creates the `AtlasServer` entity, stores the change marker in its `additionalInfo.REPL_DETAILS`, and adds the server to the soft-reference attribute `replicatedTo` / `replicatedFrom` of every exported / imported entity. `skipUpdateReplicationAttr=true` leaves the entities alone. |
| `transforms` | import | Atlas `ImportTransforms` JSON, e.g. `{"hive_table": {"qualifiedName": ["replace~@cl1~@cl2"], "*": ["addClassification~Replicated"]}}`. Transformers: `replace`, `lowercase`, `uppercase`, `clearAttrValue`, `add`, `setDeleted`, `addClassification[~topLevel]`, `removeClassification`. |
| `transformers` | import | Atlas entity transformers, e.g. `[{"conditions": {"hive_db.clusterName": "EQUALS: cl1"}, "action": {"hive_db.clusterName": "SET: cl2"}}]`. Renaming `hive_db` / `hive_table` / `hive_column` / `hdfs_path` rebuilds their qualifiedNames, like Atlas' entity handlers. |
| `startGuid` / `startPosition` | import | resume an interrupted import |
| `updateTypeDefinition` | import | `false` = do not create or extend types |

Every export and import is recorded in the admin audits (`/admin/audits`) and in
`/admin/expimp/audit`. Age-out runs (`/admin/audits/ageout`) are kept as `AUDIT_REDUCTION_ENTITY_RETRIEVAL`
tasks in `/admin/tasks`.

## Authorization

`PYATLAS_AUTHORIZER=simple` is a port of Atlas' `AtlasSimpleAuthorizer` and reads the same policy file
format. A user's roles are the union of `userRoles[user]` and `groupRoles[group]` for each group in
`users-credentials.properties` (`user=GROUP1,GROUP2::hash`). A role grants:

* **admin permissions**: `admin-export`, `admin-import`, `admin-purge`, `admin-audits`
* **type permissions**: `type-read/create/update/delete`, by type category and name
* **entity permissions**: `entity-read/create/update/delete`, `entity-read/add/update/remove-classification`,
  `entity-add/remove-label` and `entity-update-business-metadata`. They are matched by entity type (super
  types included), entity id (the first unique attribute, normally `qualifiedName`), the entity's
  classifications (all of them, propagated ones included, must be allowed; super types count), and by
  label, business metadata and classification name.
* **relationship permissions**: `add/update/remove-relationship`, by relationship type and both ends.

Patterns are Java-style regular expressions matched against the whole value (`.*` matches everything),
case-insensitive equality also matches. The checks are made where Atlas makes them, and give
`403 ATLAS-403-00-001 "<user> is not authorized to perform <action>"`:

* Admin endpoints check the same privileges as `AdminResource`.
* The type store and entity store check the type and entity privileges.
* Relationship CRUD checks the relationship privileges.
* Lineage checks `entity-read` on the start entity.
* Search results, lineage maps and `bulk/headers` are *scrubbed*: an entity the user may not read keeps
  its type only, with guid `-1`, like in Atlas.
* `GET /admin/session` reports `atlas.entity.create/update.allowed`, which the UI uses to show or hide
  its edit buttons.

Imports skip the entity and type checks, like Atlas; `admin-import` is required instead.

The bundled `conf/atlas-simple-authz-policy.json` is Atlas' default policy (`ROLE_ADMIN`, `DATA_STEWARD`,
`DATA_SCIENTIST`) with one addition: `DATA_STEWARD` and `DATA_SCIENTIST` also get `type-read`. Atlas'
default grants it to neither, which leaves their UI without any types. The user `admin` is mapped to
`ROLE_ADMIN`.

## Security

* **Authentication.** Users come from `users-credentials.properties`; use BCrypt hashes
  (`python scripts/hash_password.py <user> <groups>`) and change the default `admin`/`admin` (pyatlas logs a
  warning while it is unchanged). After `PYATLAS_LOGIN_MAX_FAILURES` failed logins, a user name is locked
  for a while for that client address.
* **Sessions.** The UI session is a signed cookie (`ATLASSESSIONID`, `HttpOnly`, `SameSite=Lax`). Set
  `PYATLAS_SESSION_SECRET` to a long random value. Anyone who knows the key can forge sessions, so
  published example values are refused. Sessions expire after `PYATLAS_SESSION_MAX_AGE_SECS`. A user
  removed from the users file loses access immediately, and groups always come from the current file.
* **CSRF.** Like Atlas, data-changing API calls from browsers need the per-session token from
  `GET /admin/session` in the `X-XSRF-HEADER` header; both bundled UIs send it. API clients that are not
  browsers (curl, Python) are not affected.
* **Authorization.** Every REST call is checked by the Atlas simple authorizer (see *Authorization*).
  Saved searches are private to their owner, and download files to the user who created them.
* **Input handling.** No user input is evaluated. Elasticsearch queries are built as structured JSON, never as
  query strings; wildcard values are escaped. File downloads resolve names within the user's own directory
  only. `POST /admin/importfile` reads only below `PYATLAS_IMPORT_DIR`. Request bodies are limited
  (`PYATLAS_MAX_UPLOAD_MB`), import ZIPs and XLSX uploads are checked against zip bombs, and XLSX parsing
  uses `defusedxml`. CSV/XLSX exports prefix values that would run as spreadsheet formulas with `'`.
* **Responses** carry Atlas' security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options`, a
  Content-Security-Policy; `Strict-Transport-Security` with `PYATLAS_HSTS=true`). Internal errors return
  only an error id; the details go to the server log.
* **Deployment.** Put pyatlas behind HTTPS (reverse proxy) and set `PYATLAS_SESSION_COOKIE_SECURE=true` and
  `PYATLAS_HSTS=true`. Keep Elasticsearch on a private network or enable its security and pass credentials
  (`PYATLAS_ES_USERNAME`/`PASSWORD`, `PYATLAS_ES_API_KEY`). The docker-compose file disables Elasticsearch
  security and opens ports 9200/5601 for local development only.

## How the Atlas model is stored in Elasticsearch

| Index | One document per | Notes |
|---|---|---|
| `atlas_typedefs` | type definition | Source of truth for the type system. Every node keeps a resolved in-memory `TypeRegistry` and reloads it when another node changes typedefs. |
| `atlas_entities` | entity | Raw Atlas JSON (attributes, classifications, business metadata; stored but not indexed) plus search fields: system attributes, `displayText`, `fulltext`, typed attribute groups and nested `tags`. |
| `atlas_relationships` | relationship instance | The graph edges: `end1Guid`/`end2Guid`, type, label, `propagateTags`, status, attributes. |
| `atlas_unique` | unique attribute value | The document id is a hash of *(type, attribute, value)*. Creating it with `op_type=create` makes unique attributes such as `qualifiedName` atomic. |
| `atlas_audit` | audit event | `EntityAuditEventV2` |
| `atlas_meta` | misc. | applied model patches, typedef version, saved searches |

Indexed attribute values live in typed groups (`idx.str.<attr>`, `idx.lng.<attr>`,
`idx.dbl.<attr>`, `idx.bool.<attr>`). Attributes that share a name but have different types in
different entity types therefore never clash in the Elasticsearch mapping. String attributes get
three fields:

* a `keyword` for exact matching and sorting
* a lower-cased `.lc` keyword for case-insensitive operators
* an analysed `.text` field for full-text search, which splits `snake_case`, `camelCase` and dotted names

### Behaviour compared to Apache Atlas

* **Transactions.** Elasticsearch has no multi-document transactions. A mutation is validated
  completely before anything is written. Unique attribute values are reserved atomically, and
  existing entity documents are written with optimistic concurrency (`if_seq_no`). A conflicting
  concurrent update fails with `ATLAS-409-00-00B` instead of blocking.
* **Classification propagation** is recomputed per *(source entity, classification)* with a
  breadth-first walk over the relationship index, synchronously after each mutation. Atlas' async
  "tasks" mode is not used.
* **Unique attributes** are unique per entity type, and lookups by unique attribute also search
  sub-types (for example `DataSet` → `hive_table`). Soft-deleted entities release their unique
  values, as in Atlas.
* **Soft delete** is the only delete mode. `PUT /api/atlas/admin/purge` hard-deletes entities that
  are already soft-deleted.
* **Basic-search string operators** (`=`, `!=`, `startsWith`, `contains`, `like`, …) are
  case-insensitive.

## Project layout

```
pyatlas/
  config.py            settings
  main.py              FastAPI app factory, UI serving, error handling
  auth.py              file-based auth, UI login/session, Basic auth
  services.py          wiring, metrics, DSL entry point
  store/               Elasticsearch access + index mappings (+ in-memory emulation)
  typesystem/          type registry, value validation, typedef store + model loader/patches
  repository/          entity/relationship store, propagation, audit, JSON converters
  discovery/           basic/quick/relationship search, filters, DSL subset, lineage, saved searches
  web/                 REST routers (types, entity, relationship, search, lineage, glossary, admin)
parity/              migration checks against the old Aurelius stack (python -m parity)
models/                Atlas model JSON files (from Apache Atlas) + 9000-Aurelius (m4i types)
ui/                    pre-built Atlas UIs (classic + React `n3/`), from Apache Atlas
conf/                  users file
tests/                 API tests (run against the in-memory store)
```

## Rebuilding the bundled UIs

The UIs were built from the Apache Atlas repository:

* classic UI: `dashboardv2`, `npm install && npm run build` → `ui/`
* React UI: `dashboard`, `npm install && npm run build` → `ui/n3/`

Copy the new build output over `ui/` to upgrade.

## License

Apache License 2.0. The bundled Atlas models and UIs are Apache Atlas material; see `NOTICE`.
