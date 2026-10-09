# aurelius-atlas-testing

Traceability for Aurelius Atlas ([ADR 049](../../../docs/architecture/adr/049-every-function-and-rule-is-traceable-to-a-test.md)):
every public function and every specified rule must be named by a test.

## In tests

The pytest plugin is installed with the workspace and registers two markers:

```python
import pytest


@pytest.mark.covers("aurelius_atlas_store_es.indices.index_name", rules=["ESI-04"])
def test__index_name_joins_prefix_and_kind(settings): ...


@pytest.mark.component  # needs Docker
async def test__component_health_of_real_node(live_settings): ...
```

A test may carry several `covers` markers. `--traceability-out=FILE` writes every test's declarations
and outcome to `FILE` (the `ci` configuration of each Python `test` target sets it).

## The check

```bash
uv run python -m aurelius_atlas_testing.check            # exit 1 and list the gaps
nx check aurelius-atlas-test-report                      # the same, as CI runs it
```

It inventories the public API of the projects listed in the root `pyproject.toml`
(`[tool.aurelius-atlas.traceability]`), reads the rules of every increment specification, collects
every project's tests, and reports uncovered functions, uncovered rules, and declarations that point
at nothing. What counts as a public function is DD-006.
