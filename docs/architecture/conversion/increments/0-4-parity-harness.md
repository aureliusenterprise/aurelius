# 0.4 Parity harness

- **Status:** in review
- **Records:** ADR 048 (stays Proposed until the first fixture is recorded), DD-008, DD-009

## Scope

- `libs/python/aurelius-atlas-parity`: scenario files, a JSON path language, normalisation, recording
  fixtures from the reference, comparing a candidate with them, and the `parity-results.json` format
  shown by the test report.
- `dev/atlas-reference`: builds and runs Apache Atlas 2.4.0 from its source tag with Atlas's own Docker
  set-up, for recording.

Not in scope: scenarios and fixtures for real endpoints (they arrive with each REST increment, the first
in 0.5).

## Semantics

| Id     | Rule                                                                                                                                                                        | Verified by |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| PAR-01 | A scenario's name equals its file name; step names are unique; request paths start with `/`; every path and deviation id is well formed                                     |             |
| PAR-02 | `${name}` in a request's path, query or body is replaced by a value captured earlier in the scenario or by `run`; an unknown name fails the step                            |             |
| PAR-03 | Normalisation removes ignored paths, masks timestamp keys at any depth, sorts unordered lists, and numbers GUIDs in values and keys by first appearance across the scenario |             |
| PAR-04 | Recording stores, per step, the endpoint, status code and normalised body; if any step fails, nothing is recorded                                                           |             |
| PAR-05 | Equal answers _match_; differences only under allowed paths are a _deviation_ naming the ids; anything else, including another status code, is a _mismatch_                 |             |
| PAR-06 | Without a fixture, or with one recorded for other steps, every step is _not recorded_ and the parity test is skipped                                                        |             |
| PAR-07 | A step that cannot be executed is an _error_, and the steps after it are _error_ "not executed"                                                                             |             |
| PAR-08 | Every deviation id a scenario cites is defined in `deviations.md`                                                                                                           |             |
| PAR-09 | Fixtures are written as indented, key-sorted JSON                                                                                                                           |             |
| PAR-10 | Paths support `$`, `.member`, `[*]`, `[n]` and `..key`; anything else is refused                                                                                            |             |
| PAR-11 | `nx build-atlas` and `nx up aurelius-dev-atlas-reference` produce an Atlas 2.4.0 answering on port 21000                                                                    | gate        |

PAR-11 is not run in CI (the reference is only needed to record); it is verified by recording the first
fixture.

## Java origin

None. The reference set-up reuses Atlas's `dev-support/atlas-docker`.

## Deviations

None.

## Acceptance

```bash
uv run pytest libs/python/aurelius-atlas-parity/tests
nx build-atlas aurelius-dev-atlas-reference && nx up aurelius-dev-atlas-reference   # manual, once
```
