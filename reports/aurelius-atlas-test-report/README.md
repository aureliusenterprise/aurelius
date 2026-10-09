# aurelius-atlas-test-report

One page that shows what a change proves (ADR 049): test results per project, failing tests,
traceability of every specified rule and every public function to the tests that name them,
parity with the reference Atlas (ADR 048), and line and branch coverage.

## Usage

```bash
nx run-many -t test -c ci                  # writes junit.xml, coverage.xml, traceability.json per project
nx check aurelius-atlas-test-report        # fails when a function or rule has no test; writes dist/analysis.json
nx render aurelius-atlas-test-report       # renders dist/index.html, dist/summary.md, dist/report.json
```

The report reads every `junit.xml`, `e2e-junit.xml`, `coverage.xml`, `traceability.json` and
`parity-results.json` under the workspace (ignoring `node_modules`, `.venv` and `dist`). Without test
results it still renders the traceability, with every test marked _not run_.

In CI the report is uploaded as the `test-report` artifact and its summary is added to the job summary.
