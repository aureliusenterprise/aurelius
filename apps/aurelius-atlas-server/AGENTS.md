# aurelius-atlas-server

The Atlas REST API. This file covers wiring specific to this app; workspace-wide rules live in the
root `AGENTS.md` (read its Conversion Workflow before adding an endpoint).

## Layout

- `aurelius_atlas_server/` — the package (`python -m aurelius_atlas_server`)
    - `app.py` — app factory; the store client lives on `app.state.store` for the app's lifetime
    - `settings.py` — `ServerSettings` (env prefix `AURELIUS_ATLAS_SERVER_`, `__` for nesting)
    - `errors.py` — Atlas error codes and the `{"errorCode", "errorMessage"}` answer
    - `routes/` — one module per Atlas REST resource (`AdminResource` → `admin.py`)
- `tests/` — unit tests; `tests/parity/` — parity scenarios, fixtures, normalisation rules and the
  parity test (marked `component`, needs Docker)

## Wiring Checklist

- New endpoint: a semantics spec rule, a route, a unit test and a parity scenario naming the rule;
  record its fixture (`nx record-parity`) or leave it _not recorded_ (the report shows it).
- New error code: add it to `errors.py` with the exact Atlas code and message from `AtlasErrorCode`.
- `implicitDependencies` include `aurelius-dev-elasticsearch` (serve) and the libraries it imports.
- Port 21000 is shared with `apps/aurelius-atlas-dashboard/nginx.conf` (a test checks it).

## Commands

```bash
nx serve aurelius-atlas-server
nx test aurelius-atlas-server -c ci
uv run pytest apps/aurelius-atlas-server/tests -m "not component"   # offline
nx record-parity aurelius-atlas-server
```

## Conventions

- Routers stay thin; behaviour goes into the libraries (`aurelius-atlas-core` from increment 1.x).
- Answers keep Atlas's exact JSON field names and status codes; any difference is a deviation
  with an id in `deviations.md` and an allowance in the scenario.

## Removal

Part of the spine (ADR 050).
