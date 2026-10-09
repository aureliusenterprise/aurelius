# aurelius-atlas-parity

Parity harness: scenarios, normalisation, recording and comparison. This file covers wiring
specific to this lib; workspace-wide rules live in the root `AGENTS.md` and `libs/python/AGENTS.md`.

## Layout

- `scenario.py` — the scenario model and YAML loading
- `paths.py` — the small JSON path language used everywhere
- `normalise.py` — what may differ between runs (DD-008)
- `compare.py` — differences and the match/deviation/mismatch decision
- `runner.py` — sending requests, recording fixtures, comparing
- `results.py` — the `parity-results.json` format the test report reads
- `pytest_support.py`, `cli.py` — test helpers; `python -m aurelius_atlas_parity record`

## Wiring Checklist

- `reports/aurelius-atlas-test-report` re-exports `results.py`; changing the format changes
  the report.
- Deviation ids cited by scenarios must exist in `docs/architecture/conversion/deviations.md`
  (`unknown_deviations` checks it).

## Commands

```bash
uv run pytest libs/python/aurelius-atlas-parity/tests
uv run python -m aurelius_atlas_parity record --help
```

## Conventions

- Never weaken a comparison to make a test pass: either fix the behaviour, or record a
  deviation in `deviations.md` and allow it at the narrowest path.
- Normalisation rules are reviewed like code: each one hides a class of differences.

## Removal

Part of the workflow (ADR 048).
