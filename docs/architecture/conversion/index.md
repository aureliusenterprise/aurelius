# Conversion

Aurelius Atlas re-implements Apache Atlas 2.4.0 in Python with Elasticsearch 9 as its only store,
keeping the REST API and the dashboard ([ADR 046](../adr/046-the-catalogue-keeps-its-public-contract.md),
[ADR 047](../adr/047-one-search-store-is-the-system-of-record.md)). The work proceeds in increments
([ADR 051](../adr/051-the-conversion-proceeds-in-specified-increments.md)); this page is the roadmap and
the status of each one.

The ledger in this section is the central record of the conversion:

| Page                                            | What it holds                                                          |
| ----------------------------------------------- | ---------------------------------------------------------------------- |
| [Design Log](./design-log.md)                   | Numbered technical decisions (`DD-NNN`), never edited once accepted    |
| [Java to Python Map](./java-map.md)             | Which Java module or class becomes which Python module, and its status |
| [Deviations from Apache Atlas](./deviations.md) | Every intended behaviour difference, referenced by the parity report   |
| [Increments](./increments/index.md)             | The semantics specification of each increment                          |

## Definition of done for an increment

- [ ] Semantics spec in `increments/`, every rule has an id
- [ ] Every new public function has a test that names it (`@pytest.mark.covers`)
- [ ] Every rule id is named by at least one test
- [ ] Parity scenarios for the endpoints in scope pass against the recorded reference
- [ ] `nx affected -t lint typecheck test e2e -c ci` is green and the coverage gate holds
- [ ] Design log, Java map and deviations updated; ADR written if a business-level decision was made
- [ ] The test report shows the increment's rules and endpoints as green
- [ ] Conventional-commit title and two human approvals

## Roadmap

Status values: _planned_, _in progress_, _in review_, _done_.

| #   | Increment                       | Semantics in scope                                                                  | Java origin                                    | Status    |
| --- | ------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------- | --------- |
| 0.1 | Adopt the template              | Remove unused slices, rename, ADRs 046–051, this ledger                             | –                                              | in review |
| 0.2 | Elasticsearch infrastructure    | `dev/elasticsearch`, store library skeleton, health check                           | –                                              | in review |
| 0.3 | Test report and traceability    | `covers` marker, function-to-test checker, HTML test report in CI                   | –                                              | in review |
| 0.4 | Parity harness                  | Reference Atlas container, scenario format, recorder, normaliser, replay            | –                                              | in review |
| 0.5 | Server and dashboard skeleton   | Admin version/session/status endpoints, dashboard served; template examples removed | `AdminResource` (part)                         | planned   |
| 1.1 | Typedef models                  | Enum, struct, classification, entity, relationship, business-metadata definitions   | `intg/.../model/typedef`                       | planned   |
| 1.2 | Type registry                   | Attribute types, supertypes, constraints, validation errors                         | `AtlasTypeRegistry`, `AtlasStructType`, …      | planned   |
| 1.3 | Typedef storage and bootstrap   | Typedef index, built-in models at start-up, typedef versions                        | `AtlasTypeDefGraphStore`, model patches        | planned   |
| 1.4 | Types REST                      | `/v2/types/...` read and write                                                      | `TypesREST`                                    | planned   |
| 2.1 | Entity models and validation    | `AtlasEntity`, extended info, headers, validation                                   | `intg/.../model/instance`, `AtlasEntityType`   | planned   |
| 2.2 | Entity store                    | Index layout, GUIDs, unique attributes, optimistic versioning                       | `AtlasEntityStoreV2`                           | planned   |
| 2.3 | Entity read REST                | By GUID, by unique attributes, bulk, headers                                        | `EntityREST`                                   | planned   |
| 2.4 | Entity write REST               | Create/update, partial update, bulk                                                 | `EntityREST`, `EntityGraphMapper`              | planned   |
| 2.5 | Delete semantics                | Soft and hard delete, purge                                                         | `DeleteHandlerV1`, `SoftDeleteHandlerV1`       | planned   |
| 3.1 | Relationship instances          | Relationship CRUD and relationship attributes                                       | `RelationshipREST`, `AtlasRelationshipStoreV2` | planned   |
| 3.2 | Ownership cascades              | Composition and owned-reference cascades                                            | `DeleteHandlerV1`                              | planned   |
| 3.3 | Direct classifications          | Add, update, remove, validity periods                                               | `EntityREST`                                   | planned   |
| 3.4 | Classification propagation      | Propagation, blocked propagation, removal                                           | `ClassificationPropagateTaskFactory`           | planned   |
| 3.5 | Entity audit                    | Audit events and audit REST                                                         | `EntityAuditRepository`                        | planned   |
| 4.1 | Basic search                    | `SearchParameters`, filters, operators, sort, paging                                | `EntitySearchProcessor`, `SearchContext`       | planned   |
| 4.2 | Quick search and suggestions    | Free text, facets, suggestions                                                      | `AtlasDiscoveryService`                        | planned   |
| 4.3 | DSL parser                      | Atlas DSL grammar to AST                                                            | `AtlasDSLParser.g4`, `query/`                  | planned   |
| 4.4 | DSL execution                   | AST to search queries; declared unsupported forms                                   | `GremlinQueryComposer` (replaced)              | planned   |
| 4.5 | Saved searches and user profile | Saved search CRUD                                                                   | `UserProfileService`                           | planned   |
| 5.1 | Lineage                         | Process inputs/outputs, depth, direction, on-demand lineage                         | `EntityLineageService`                         | planned   |
| 5.2 | Glossary                        | Glossaries, terms, categories, term assignment                                      | `GlossaryREST`, `GlossaryService`              | planned   |
| 5.3 | Business metadata and labels    | Business metadata attributes, labels                                                | `EntityREST`                                   | planned   |
| 6.1 | Authentication                  | Keycloak OIDC, session endpoints                                                    | `AtlasKeycloakAuthenticationProvider`          | planned   |
| 6.2 | Authorization                   | Simple authorizer policies on every endpoint                                        | `atlas-simple-authz-policy`                    | planned   |
| 6.3 | Import, export and migration    | Atlas export ZIP format, migration of an existing Atlas                             | `ExportService`, `ImportService`               | planned   |
| 6.4 | Hardening                       | Metrics, observability, load test, index tuning                                     | `AdminResource` metrics                        | planned   |
