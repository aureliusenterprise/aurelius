# aurelius-fastapi-example

Example FastAPI backend service demonstrating the Aurelius Python service pattern:
Keycloak-secured CRUD over a SQLModel entity, Postgres change-data-capture streamed
to clients via SSE, and Logfire/OpenTelemetry telemetry.

Part of the template **spine**.

## Features

- `GET /entities/` — paginated list with `plainto_tsquery` full-text search
- `GET /entities/{guid}` — single entity
- `PUT /entities/` — upsert
- `DELETE /entities/{guid}` — delete (returns 410 when already gone)
- `GET /entities/sse` — live change notifications from Postgres `LISTEN/NOTIFY`
- `GET /health/ready` — readiness probe (excluded from the OpenAPI schema)

## How it works

- `app.py` builds the app via a factory with a lifespan that creates the schema in
  development and starts the CDC notification broadcaster.
- `providers/` holds data access and external clients; `auth.py` validates Keycloak
  JWTs via JWKS behind a `pybreaker` circuit breaker.
- Settings are pydantic `BaseSettings` fed from `.env` (dev defaults) and `.env.enc`
  (SOPS-encrypted, injected by the `decrypt` target).

## Workspace dependencies

- `aurelius-example` — the shared `Entity` model
- `aurelius-sdk[postgresql]` — Postgres listener and helpers
- Dev infra (started automatically by `serve`): Keycloak, Postgres, observability

## Running

```bash
nx serve aurelius-fastapi-example   # starts Keycloak, Postgres, observability first
```

Serves on `127.0.0.1:8000`. Configuration keys come from `.env` (dev defaults)
and `.env.enc` (SOPS-encrypted).

## Testing

```bash
uv run pytest tests            # unit tests
nx e2e aurelius-fastapi-example  # testcontainers-based E2E (builds the image)
```
