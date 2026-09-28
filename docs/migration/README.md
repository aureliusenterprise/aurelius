# Aurelius on pyatlas: migration

Apache Atlas, Kafka, the three Flink jobs and the Python back ends are replaced by pyatlas
(`backend/pyatlas`), a Python port of Atlas on Elasticsearch. The frontend (`apps/atlas`), Keycloak and the
reverse proxy stay. Decisions (28 Sep 2026): big-bang cutover, pyatlas inside this monorepo, only `apps/atlas`
in scope, the Kafka data dictionary harvester switched off.

## Phase 0 - foundation (this branch: `pyatlas-migration`)

| Deliverable | Where | Status |
| --- | --- | --- |
| pyatlas in the monorepo, Nx project, repo-root Docker context | `backend/pyatlas`, `project.json` | done |
| m4i type definitions as pyatlas models | `backend/pyatlas/models/9000-Aurelius`, `scripts/gen_m4i_models.py` | done, all 39 Aurelius types equal to the deployed ones |
| Check 1 - stored data | `python -m parity store` | done |
| Check 2 - search and quality indices | `python -m parity dump` / `indices` | done (used from phase 2) |
| Check 3 - same changes, same results | `python -m parity mutate` / `compare-mutations` | done |
| Check 4 - API responses | `python -m parity replay` (HAR, JSONL, access log) | done |
| Check 5 - user journeys | `apps/atlas-e2e` (Playwright) | written; to be validated against the current stack in phase 1 |
| Quality rules without `eval` | `python -m parity rules` | done: grammar fixed, all usable rules fit |
| Kafka inventory | [kafka-inventory.md](kafka-inventory.md) | done; all Kafka uses removed (decided 28 Sep 2026) |
| Staging next to the old stack | `backend/pyatlas/docker-compose.parity.yml` | done |

Every check writes `report.md` + `report.json` to `parity-reports/` and exits with 1 on differences, so it can
gate CI. The comparison rules (accepted differences) are in `backend/pyatlas/parity/allowlists/`.

## Phase 1 - Keycloak and the frontend on pyatlas

| Deliverable | Where | Status |
| --- | --- | --- |
| Keycloak access tokens in pyatlas (JWKS, issuer, expiry, optional client check; realm roles -> groups) | `backend/pyatlas/pyatlas/oidc.py`, `PYATLAS_OIDC_*` | done, 14 tests |
| Realm `m4i` for development (client `m4i_atlas`, 3 roles, 3 demo users) | `dev/pyatlas/keycloak/realm-m4i.json` | done |
| Reverse proxy image with the frontend built from this repo | `dev/pyatlas/reverse-proxy` | done |
| Local stack: proxy, Keycloak 22, pyatlas, Elasticsearch | `dev/pyatlas/docker-compose.yml`, `start.bat` | done |
| Clickstream and error reports of the frontend | `/api/aurelius/repository/{log,error}` | done (logged as JSON lines) |

Verified end to end with the built frontend, Keycloak 22.0.5, Apache httpd and pyatlas: login through the Aurelius
login page, token validation, entity editing by a data steward (saved as that user). The pages built on search
need phase 2.

Found on the way: a client that requires PKCE breaks the frontend's keycloak-js setup (the realm leaves PKCE
optional), and a server-wide `ProxyPassReverseCookiePath` rewrote Keycloak's session cookies (now scoped to
`/aurelius/atlas2/`).

## What phase 0 found

1. **Entity `attributes` lacked relationship-backed references** (fixed in pyatlas). Atlas also returns
   reference attributes that are stored as relationships, such as `steward`, `dataEntity`, `fields`, in
   `attributes`, not only in `relationshipAttributes`. For attributes inherited from a supertype it returns them
   empty (`source` on every m4i type). pyatlas now does the same; found by check 1 on the sample export.
2. **Attribute multiplicity defaults** (fixed in pyatlas). A SET/LIST attribute without `valuesMaxCount` gets
   `2147483647` as in Atlas (it was 1). Attribute definitions also drop the properties Atlas does not store
   (`relationshipTypeName`, `isLegacyAttribute`).
3. **m4i-atlas-core differs from the deployed types** in two places: `m4i_generic_process.definition` exists
   only in the deployed type, and `m4i_field` labels `definition` as "Data Type" in m4i-atlas-core. The model
   files follow the deployed types (`DEPLOYED_OVERRIDES` in the generator); m4i-atlas-core should be corrected.
4. **Code injection in today's quality rules.** `validate_function_string` only checks the names of the
   outermost code object, so an expression such as `completeness((lambda: ...)())` passes and `eval` then runs
   arbitrary Python (reachable via `object.__subclasses__()` although builtins are removed). Anyone who can
   write an `expression` attribute of a data quality entity can run code in the quality jobs. pyatlas (phase 3)
   parses expressions with a fixed grammar instead. Of 1,842 expressions in the repository and sample data,
   1,812 fit it. The other 30 (15 distinct) use capitalised names such as `Completeness(...)` and are rejected
   by today's validator as well.
5. **The golden App Search documents belong to the sample export**: every document of `atlas-dev.json` is an
   entity of `sample_data.zip`, so the pair is the regression oracle for phase 2.

## Running the checks

```bash
cd backend/pyatlas
python -m parity rules --repo-defaults
python -m parity store --zip ../m4i-atlas-post-install/data/sample_data.zip \
    --right http://localhost:21100 --right-user admin --right-password admin
python -m parity dump --source es:https://old-es:9200#.ent-search-engine-documents-atlas-dev --out old-atlas-dev.json
python -m parity mutate --right https://old/aurelius/atlas2 --right-token "$TOKEN" --out old.json
python -m parity mutate --right http://localhost:21100 --right-user admin --right-password admin --out new.json
python -m parity compare-mutations old.json new.json
python -m parity replay --recording session.har --right http://localhost:21100 --rewrite aurelius
```

On Windows without Python: `backend\pyatlas\run_parity.bat <same arguments>` (URLs of services on the same
machine: `http://host.docker.internal:<port>`).
