# aurelius-atlas-parity

Parity testing ([ADR 048](../../../docs/architecture/adr/048-behaviour-is-proven-against-the-reference-before-it-is-accepted.md)):
the same HTTP calls are sent to the reference Apache Atlas once, to **record** its answers, and to
Aurelius Atlas on every test run, to **compare** with that recording.

## Scenarios

A scenario is a YAML file of steps (see `aurelius_atlas_parity.scenario` for every field):

```yaml
name: entity-roundtrip
description: Create an entity and read it back.
steps:
    - name: create
      request:
          method: POST
          path: /api/atlas/v2/entity
          json: { entity: { typeName: DataSet, attributes: { qualifiedName: "q-${run}" } } }
      capture: { guid: "$.mutatedEntities.CREATE[0].guid" }
    - name: read
      request: { method: GET, path: "/api/atlas/v2/entity/guid/${guid}" }
      unordered: ["$.entity.labels"]
      deviations:
          - { path: "$.entity.attributes.owner", id: DV-07 }
```

## Normalisation

Before comparing, both answers are normalised (DD-008): ignored paths removed, timestamps masked,
unordered lists sorted, and GUIDs numbered `<guid-1>`, `<guid-2>`, … by first appearance across the
scenario, so the reference and the candidate may assign different GUIDs but must link them the same way.

## Recording

```bash
nx up aurelius-dev-atlas-reference
uv run python -m aurelius_atlas_parity record --scenarios <dir> --fixtures <dir> --rules <rules.yaml>
```

Fixtures are key-sorted JSON, committed and reviewed like code.

## Comparing in tests

```python
from aurelius_atlas_parity.pytest_support import check_results
from aurelius_atlas_parity.runner import compare, load_fixture

results = compare(client, scenario, load_fixture(fixtures, scenario), rules)
parity_log.add(results)  # a session-wide ParityLog writes parity-results.json for the report
check_results(results)  # skips when not recorded, fails on mismatch or error
```
