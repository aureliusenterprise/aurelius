# 0.2 Elasticsearch infrastructure

- **Status:** in review
- **Records:** ADR 047 (now Accepted), DD-003, DD-004, DD-005

## Scope

- `dev/elasticsearch`: a single-node Elasticsearch 9.1.5 with security on, started by `nx serve` / `nx up`
  like every other dev infrastructure project.
- `libs/python/aurelius-atlas-store-es`: connection settings, client creation, health check, index
  naming, and a disposable test node for component tests.

Not in scope: index mappings and any Atlas data (typedefs in 1.3, entities in 2.2, relationships in 3.1).

## Semantics

| Id     | Rule                                                                                                      |
| ------ | --------------------------------------------------------------------------------------------------------- |
| ESI-01 | Default settings reach the local dev node (`http://localhost:9200`) as user `elastic` with prefix `atlas` |
| ESI-02 | Username and password are set together or not at all; the password never appears in a representation      |
| ESI-03 | Index prefixes are lower-case, start with a letter, and have at most 32 characters                        |
| ESI-04 | Every index name is `<prefix>-<kind>`; kinds are lower-case letters, digits and underscores               |
| ESI-05 | The client uses exactly the configured hosts, credentials, timeout and TLS settings                       |
| ESI-06 | The health check reports cluster name, status and node count, waiting for the requested status            |
| ESI-07 | A `red` cluster is reported, not raised, and counts as unavailable; `green` and `yellow` are available    |
| ESI-08 | An unreachable cluster or an error answer (including rejected credentials) raises `StoreUnavailableError` |

## Java origin

None directly. It replaces the role of Atlas's `graphdb` module and its HBase/Solr configuration
(`atlas-application.properties`: `atlas.graph.storage.*`, `atlas.graph.index.search.*`).

## Deviations

None visible to clients.

## Acceptance

- Unit tests: `uv run pytest libs/python/aurelius-atlas-store-es/tests -m "not component"`
- Component tests (Docker): `uv run pytest libs/python/aurelius-atlas-store-es/tests -m component`
- Dev node: `nx up aurelius-dev-elasticsearch`, then
  `curl -u elastic:changeme http://localhost:9200/_cluster/health` answers `green`.
