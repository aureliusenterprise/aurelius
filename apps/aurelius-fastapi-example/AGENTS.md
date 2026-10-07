# aurelius-fastapi-example

Example FastAPI backend service. This file covers wiring specific to this app;
workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `aurelius_fastapi_example/` — the package (run with `uv run python -m aurelius_fastapi_example`)
    - `app.py` — FastAPI app factory and middleware wiring
    - `__main__.py` — uvicorn entry point
    - `globals.py` — process-wide singletons (settings, DB, clients)
    - `models.py` — pydantic models and `BaseSettings` (env-backed config)
    - `routes/` — routers, one module per resource
    - `providers/` — data access and external service clients
- `tests/` — unit tests (`test__*.py`, mirrors package layout, `conftest.py` fixtures)
- `e2e/` — pytest + testcontainers E2E tests with their own `docker-compose.yaml`

## Configuration

- Settings are a pydantic `BaseSettings` in `models.py`; every key comes from `.env`.
- When adding a setting: add it to the settings model, to `.env` (dev default),
  and run the encrypt `nx encrypt` target for this project.

## Wiring Checklist

When changing this app, check all of:

- `project.json` — `implicitDependencies` and `serve` `dependsOn` (Keycloak,
  Postgres, observability). Adding a dependency here changes what `nx serve` starts.
- `pyproject.toml` — workspace deps use `[tool.uv.sources]` with `workspace = true`;
  new libs must also be added to the root `pyproject.toml` dev group.
- `sonar-project.properties` — only touch if module paths change.
- `mkdocs.yaml` — API reference page lives at
  `docs/api-reference/apps/aurelius-fastapi-example.md`.
- `Dockerfile` and SBOM/vulnerability targets — keep in sync with new runtime deps.

## Commands

```bash
nx serve aurelius-fastapi-example        # starts Keycloak, Postgres, observability first
nx test aurelius-fastapi-example -c ci   # never without -c ci (watch mode hangs)
uv run pytest apps/aurelius-fastapi-example/tests   # fast unit run
nx e2e aurelius-fastapi-example          # builds docker image, runs testcontainers
nx lint aurelius-fastapi-example
```

## Conventions

- Routers stay thin; logic goes in `providers/`. Raise `HTTPException` in routes only.
- All DB access goes through `aurelius_sdk.postgresql` / SQLModel, never raw connections.
- Outbound calls use `pybreaker` circuit breakers (see `globals.py`) and `httpx`.
- Responses use the generic `Envelope`/`PaginatedResponse` models in `models.py`.
- New routes need both a unit test in `tests/routes/` and coverage in `e2e/`.

## Removal

This app is part of the spine. If a fork removes it, also remove: the frontend's
`implicitDependencies`/`dependsOn` reference, its `mkdocs.yaml` nav entry, the root
`pyproject.toml` uv member and dev-group entry, and `dev/keycloak` client config.
