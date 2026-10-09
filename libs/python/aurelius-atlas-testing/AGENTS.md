# aurelius-atlas-testing

Traceability tooling: the `covers` marker plugin, API inventory, specification parser and
gap check. This file covers wiring specific to this lib; workspace-wide rules live in the
root `AGENTS.md` and `libs/python/AGENTS.md`.

## Layout

- `aurelius_atlas_testing/plugin.py` — pytest plugin (entry point `pytest11`), markers and `--traceability-out`
- `markers.py`, `records.py` — the marker contract and the traceability file format
- `inventory.py` — public API from source (`ast`), see DD-006
- `specs.py` — rules from `docs/architecture/conversion/increments/*.md`
- `analysis.py`, `check.py`, `workspace.py` — joining everything; CLI; workspace guards

## Wiring Checklist

- Registered in root `pyproject.toml` (member, dev group, `uv.sources`); the dev group
  install is what makes the plugin active in every project.
- The root `pyproject.toml` table `[tool.aurelius-atlas.traceability]` lists the traced
  projects and the specification directory.
- This project loads its own plugin from `tests/conftest.py` and disables the entry point
  (`addopts`), so coverage measures the plugin's import; do not remove either.

## Commands

```bash
uv run pytest libs/python/aurelius-atlas-testing/tests
uv run python -m aurelius_atlas_testing.check
```

## Conventions

- Changing the marker contract or the specification format changes every project's tests
  and every spec: write a design-log entry first.
- Keep it free of Atlas domain code; it must stay usable before any Atlas code exists.

## Removal

Part of the workflow (ADR 049).
