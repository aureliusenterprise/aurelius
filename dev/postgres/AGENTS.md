# aurelius-dev-postgres

Local development Postgres. This file covers wiring specific to this project;
workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — single Postgres service
- `.env` / `.env.enc` — SOPS-encrypted dev settings (credentials, port)

## Wiring Checklist

- Exposes the external Docker network `aurelius-dev-postgres-network`; the
  FastAPI example and the JDBC sink connector attach to it.
- The FastAPI example's `serve` target starts this project via `dependsOn`.
- Database `aurelius`, credentials from `.env` dev defaults — the same values
  the FastAPI example's settings model reads.
- The `Entity` table is created by the application at startup in dev; there are
  no migration files here. After an `Entity` model change, drop/recreate the
  dev table (see `libs/python/aurelius-example/AGENTS.md`).

## Commands

```bash
nx serve aurelius-dev-postgres   # compose up (foreground)
nx up aurelius-dev-postgres      # detached, waits for healthy
```

## Conventions

- Keep it a blank database: schema belongs to the applications, not to compose
  init scripts.
- `DATABASE_PORT` (default 5432) is part of the workspace contract — coordinate
  before changing.

## Removal

Part of the spine. Removing it means replacing persistence in the FastAPI
example (and the JDBC sink's target table, if that slice is present).
