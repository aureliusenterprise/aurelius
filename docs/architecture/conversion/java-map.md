# Java to Python Map

Where each part of Apache Atlas 2.4.0 goes. Updated by every increment; the status column is the
truth about what has been ported. Status values: _not started_, _in progress_, _ported_, _replaced_
(same purpose, different mechanism), _dropped_ (not carried over; reason in
[Deviations](./deviations.md) or the design log).

## Modules

| Atlas module                    | Purpose in Atlas                                      | Target                                              | Status      |
| ------------------------------- | ----------------------------------------------------- | --------------------------------------------------- | ----------- |
| `intg`                          | Model classes, type system, client-side utilities     | `aurelius-atlas-model`, `aurelius-atlas-typesystem` | not started |
| `repository`                    | Stores, services, discovery, lineage, glossary, audit | `aurelius-atlas-core`, `aurelius-atlas-dsl`         | not started |
| `graphdb`                       | JanusGraph abstraction and implementation             | `aurelius-atlas-store-es`                           | replaced    |
| `webapp`                        | REST resources, filters, authentication               | `aurelius-atlas-server`                             | in progress |
| `server-api`                    | Interfaces shared by server components                | `aurelius-atlas-core`                               | not started |
| `common`                        | Shared utilities                                      | where used                                          | not started |
| `authorization`                 | Simple and Ranger authorizers                         | `aurelius-atlas-server` (simple authorizer only)    | not started |
| `dashboardv2`, `dashboardv3`    | Web UIs (served at `/` and `/n/`)                     | `aurelius-atlas-dashboard` (unchanged)              | in progress |
| `notification`                  | Kafka hook and entity notifications                   | –                                                   | dropped     |
| `client`                        | Java client libraries                                 | –                                                   | dropped     |
| `addons/*-bridge`, `*-shim`     | Hooks for Hive, HBase, Kafka, Sqoop, Storm, …         | –                                                   | dropped     |
| `addons/models`                 | Built-in type definitions (JSON)                      | loaded by `aurelius-atlas-core` (1.3)               | not started |
| `distro`, `build-tools`, `docs` | Packaging, build and site                             | template workflow                                   | replaced    |
| `tools/*`                       | Index repair, classification updater, analyzers       | –                                                   | dropped     |

## Classes

Rows are added by each increment for the classes it ports.

| Java class                                      | Python module                                      | Increment | Status      |
| ----------------------------------------------- | -------------------------------------------------- | --------- | ----------- |
| `web/resources/AdminResource#getVersion`        | `aurelius_atlas_server.routes.admin.version`       | 0.5       | ported      |
| `web/resources/AdminResource#getStatus`         | `aurelius_atlas_server.routes.admin.status`        | 0.5       | ported      |
| `web/resources/AdminResource#serviceLiveliness` | `aurelius_atlas_server.routes.admin.liveness`      | 0.5       | ported      |
| `web/resources/AdminResource#serviceReadiness`  | `aurelius_atlas_server.routes.admin.readiness`     | 0.5       | ported      |
| `AtlasErrorCode` (`INTERNAL_ERROR`)             | `aurelius_atlas_server.errors`                     | 0.5       | in progress |
| `web/errors/AtlasBaseExceptionMapper`           | `aurelius_atlas_server.errors.atlas_error_handler` | 0.5       | ported      |
