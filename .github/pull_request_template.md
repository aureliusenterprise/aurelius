# Increment N.M: title

<!-- PR title: conventional commit, e.g. "feat(entities): 2.3 entity read REST" -->

## Increment

- **Increment:** N.M — link to `docs/architecture/conversion/increments/N-M-slug.md`
- **Records added or relied on:** ADR NNN, DD-NNN, DV-NN

## What this change proves

<!-- The rules (ids) and endpoints this PR covers; the test report link appears in CI. -->

## Checklist

- [ ] Semantics spec written first; every rule has an id
- [ ] Every new public function and every rule id is named by a `@pytest.mark.covers` test
- [ ] Parity scenarios for the endpoints in scope pass (or the difference is a recorded deviation)
- [ ] Design log, Java map, deviations and roadmap status updated
- [ ] `nx affected -t lint typecheck test e2e -c ci` green locally or in CI
