# aurelius-atlas-test-report

Workspace-level test report. This file covers wiring specific to this project;
workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `aurelius_atlas_test_report/` — the package (`python -m aurelius_atlas_test_report`)
    - `results.py` — JUnit and Cobertura readers
    - `parity.py` — the `parity-results.json` format (written by the parity harness, 0.4)
    - `report.py` — assembling, rendering (`templates/*.j2`), writing `dist/`
- `project.json` — `check` (the traceability gate) and `render` (rendering) targets
- `dist/` — generated output (gitignored)

## Wiring Checklist

- Per-project results come from the `ci` configuration of the Python `test`/`e2e`
  targets in `tools/plugins/python.ts` (`--junitxml`, `--cov-report`, `--traceability-out`).
- The traced projects and the specification directory are configured in the root
  `pyproject.toml` under `[tool.aurelius-atlas.traceability]`.
- CI (`.github/workflows/ci.yaml`, job `test`) runs `check` after the tests and `report`
  always, then uploads `dist/` as the `test-report` artifact.

## Commands

```bash
nx check aurelius-atlas-test-report
nx render aurelius-atlas-test-report
uv run pytest reports/aurelius-atlas-test-report/tests
```

## Conventions

- This project only reads results; it never runs application tests (the `check` target
  only collects them).
- Keep the HTML self-contained (inline CSS, no CDN): the artifact is opened offline.

## Removal

Part of the workflow (ADR 049). Removing it means deleting the project, its CI steps,
and the `--junitxml`/`--traceability-out` options in `tools/plugins/python.ts`.
