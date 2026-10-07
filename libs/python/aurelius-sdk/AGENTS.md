# aurelius-sdk

Shared Python utility library (logging, cloud helpers, Postgres CDC, events,
test fixtures). This file covers wiring specific to this lib; workspace-wide
rules — including the scaffold recipe for Python libs — live in the root
`AGENTS.md` and `libs/python/AGENTS.md`.

## Layout

- `aurelius_sdk/` — the package; the root `__init__.py` is intentionally empty,
  always import from submodules (`from aurelius_sdk.logger import setup_logger`)
- `tests/test__*.py` — pytest suite
- `pyproject.toml` — extras: `logging`, `postgresql`, `aws`, `azure`, `testing`,
  `full` (base depends only on `httpx`)

## Wiring Checklist

- Registered in root `pyproject.toml` (workspace members, dev group,
  `uv.sources`) — consumed by nearly every Python project in the workspace.
- Each submodule must raise a clear error at import time when its extra is
  missing; keep the extras table in `README.md` in sync with `pyproject.toml`.
- `testing.py` (testcontainers fixtures) is shared by app unit and E2E tests —
  changing it affects every suite.

## Commands

```bash
uv run pytest libs/python/aurelius-sdk/tests
uv run pyright libs/python/aurelius-sdk
```

## Conventions

- New integrations go behind a new pip extra, never into the base dependency
  set — this lib must stay import-light.
- Apps depend on specific extras (`aurelius-sdk[postgresql]`), not `full`,
  unless they genuinely need everything.

## Removal

Part of the spine; removing it is not realistic while the FastAPI example
exists. To drop a feature, remove the submodule, its extra, and its consumers.
