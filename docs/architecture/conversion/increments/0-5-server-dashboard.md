# 0.5 Server and dashboard skeleton

- **Status:** in review
- **Records:** ADR 050 (follow-up done: template examples removed), DD-010, DV-03

## Scope

- `apps/aurelius-atlas-server`: the FastAPI app with Atlas's error format and the admin endpoints
  `version`, `status`, `liveness` and `readiness`; settings, Dockerfile, parity scenarios for the four
  endpoints (fixtures not yet recorded).
- `apps/aurelius-atlas-dashboard`: an image that builds `dashboardv2` and `dashboardv3` unchanged from the
  Atlas 2.4.0 source tag and serves them with nginx, forwarding `/api/` to the server.
- Removal of the template's examples per ADR 050: `aurelius-fastapi-example`, `aurelius-frontend-example`,
  `libs/python/aurelius-example`, the Angular libraries and brand styles, `dev/postgres`, the Avro schema,
  the Angular/Storybook/Vitest toolchain and the Chromatic CI job.

Not in scope: authentication and the `session` endpoint (6.1), metrics (6.4), UI end-to-end tests (they
need data and a session, from 1.4 and 6.1).

## Semantics

| Id     | Rule                                                                                                                                                                                                                                    | Verified by |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| ADM-01 | `GET /admin/version` answers `Version` 2.4.0, `Name` apache-atlas, Atlas's `Description`, and `Revision` = this build's revision (DV-03)                                                                                                |             |
| ADM-02 | The admin endpoints answer like Apache Atlas 2.4.0 in the parity scenarios `admin-version` and `admin-status`                                                                                                                           |             |
| ADM-03 | `GET /admin/status` answers `{"Status": "ACTIVE"}`                                                                                                                                                                                      |             |
| ADM-04 | `GET /admin/liveness` answers 200 with the text `Service is live`                                                                                                                                                                       |             |
| ADM-05 | `GET /admin/readiness` answers 200 `Service is ready to accept requests` while the store is green or yellow; otherwise 500 `ATLAS-500-00-001` "Internal server error Service not ready to accept client requests", without `errorCause` |             |
| ADM-06 | Settings come from `AURELIUS_ATLAS_SERVER_*` variables or `.env` (variables win); the store password is required; invalid settings stop start-up listing every problem                                                                  |             |
| ADM-07 | The store client opens at start-up and closes at shutdown; there are no docs pages; the OpenAPI document is at `/api/atlas/openapi.json`                                                                                                |             |
| ERR-01 | Errors answer `{"errorCode", "errorMessage"}` (plus `errorCause` only when there is one) with the code's HTTP status; `{n}` placeholders are filled in order                                                                            |             |
| DSH-01 | The dashboard image serves `dashboardv2` at `/` and `dashboardv3` at `/n/`, built from the pinned Atlas commit                                                                                                                          |             |
| DSH-02 | The dashboard forwards `/api/` to the server's port                                                                                                                                                                                     |             |

ADM-02 is named by the parity test, which is skipped until the fixtures are recorded; the report shows
those steps as _not recorded_.

## Java origin

`webapp/.../resources/AdminResource.java` (`getVersion`, `getStatus`, `serviceLiveliness`,
`serviceReadiness`), `AtlasErrorCode.INTERNAL_ERROR`, `web/errors/AtlasBaseExceptionMapper.java`,
`webapp/pom.xml` (dashboard overlays), `dashboardv{2,3}/gruntfile.js` (output paths).

## Deviations

DV-03: `Revision` reports this build, not the Atlas source commit.

## Acceptance

```bash
nx test aurelius-atlas-server -c ci            # unit + parity (parity skipped until recorded)
nx serve aurelius-atlas-server && curl http://localhost:21000/api/atlas/admin/version
nx docker-build aurelius-atlas-dashboard && nx serve aurelius-atlas-dashboard   # http://localhost:8081, /n/
nx up aurelius-dev-atlas-reference && nx record-parity aurelius-atlas-server     # once, then commit fixtures
```

The dashboard image and the reference recording need Docker Hub and the Apache archives, which were not
reachable where this increment was written; both are verified on a developer machine.
