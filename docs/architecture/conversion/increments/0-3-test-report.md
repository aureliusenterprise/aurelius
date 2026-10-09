# 0.3 Test report and traceability

- **Status:** in review
- **Records:** ADR 049 (now Accepted), DD-006, DD-007

## Scope

- `libs/python/aurelius-atlas-testing`: the `covers` and `component` pytest markers (a pytest plugin
  loaded by entry point), the public-API inventory, the specification parser, and the traceability
  check `python -m aurelius_atlas_testing.check`.
- `reports/aurelius-atlas-test-report`: one HTML page per run with test results, traceability of
  rules and functions, parity results and coverage; a Markdown summary for the CI job page.
- Nx and CI wiring: the `ci` configuration of every Python `test`/`e2e` target writes JUnit,
  coverage and traceability files; CI runs the check and publishes the report.
- Guard tests for the 0.1 rules ADO-01 and ADO-03; a _Verified by_ column for rules the gate proves.

Not in scope: comparing results with `main` over time, and publishing the report on the docs site
(see DD-007).

## Semantics

| Id     | Rule                                                                                                                                                                                       | Verified by |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| TRC-01 | A `covers` marker takes exactly one dotted target and optional rule ids like `ABC-01`; anything else stops the run naming the test                                                         |             |
| TRC-02 | With `--traceability-out`, every collected test is written with its targets, rules, component flag and outcome                                                                             |             |
| TRC-03 | A failure in any phase fails a test; a skip before the call skips it; a passing call passes it; collected only is _not run_                                                                |             |
| TRC-04 | The inventory lists public functions, public methods and properties of public classes, and classes with only private behaviour; private names, private modules and `__main__` are excluded |             |
| TRC-05 | A target names an item when it equals the item's path; a class item is also named by targets inside it                                                                                     |             |
| TRC-06 | An item or rule without naming tests is _uncovered_, with a failed naming test _failing_, otherwise _covered_; a gate rule without tests is _gate_                                         |             |
| TRC-07 | A target that names nothing in the inventory, or a rule id no specification defines, is a problem                                                                                          |             |
| TRC-08 | The check exits 1 when any item or test-verified rule is uncovered or any problem exists, else 0                                                                                           |             |
| TRC-09 | Rules are the table rows whose first cell is a rule id; ids are unique across specifications; titles start with the increment number                                                       |             |
| TRC-10 | The report shows results per project, failing tests, rules per increment, functions per project, parity and coverage, and renders without any results                                      |             |
| TRC-11 | CI fails when the check fails, and publishes the report and its summary on every run                                                                                                       | gate        |

## Java origin

None.

## Deviations

None.

## Acceptance

```bash
uv run pytest libs/python/aurelius-atlas-testing/tests reports/aurelius-atlas-test-report/tests
nx run-many -t test -c ci -p aurelius-atlas-store-es aurelius-atlas-testing aurelius-atlas-test-report
nx check aurelius-atlas-test-report     # exit 0: every function and rule named
nx render aurelius-atlas-test-report    # open reports/aurelius-atlas-test-report/dist/index.html
```
