# aurelius-atlas-store-es

Elasticsearch access for Aurelius Atlas. This file covers wiring specific to this lib;
workspace-wide rules live in the root `AGENTS.md` and `libs/python/AGENTS.md`.

## Layout

- `aurelius_atlas_store_es/` — the package; `__init__.py` is empty, import from submodules
- `tests/` — unit tests (`test__*.py`) and component tests marked `component`
  (need Docker; they start `elasticsearch_node()` from `testing.py`)

## Wiring Checklist

- Registered in root `pyproject.toml` (workspace member, dev group, `uv.sources`).
- `testing.DEFAULT_IMAGE` must match `ELASTICSEARCH_VERSION` in `dev/elasticsearch/.env`.
- `implicitDependencies` on `aurelius-dev-elasticsearch` so a change there re-runs these tests.

## Commands

```bash
uv run pytest libs/python/aurelius-atlas-store-es/tests -m "not component"   # offline
uv run pytest libs/python/aurelius-atlas-store-es/tests                      # needs Docker
uv run pyright libs/python/aurelius-atlas-store-es
```

## Conventions

- Never read environment variables here; accept `ElasticsearchSettings`.
- Every index name goes through `indices.index_name` (DD-004); never hard-code one.
- Every public function has a test marked `@pytest.mark.covers("<dotted path>")` (ADR 049).
- Storage layout decisions (mappings, ids, consistency) are design-log entries before they are code.

## Removal

Part of the spine ([ADR 047](../../../docs/architecture/adr/047-one-search-store-is-the-system-of-record.md)).
