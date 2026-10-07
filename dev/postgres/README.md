# aurelius-dev-postgres

Local development Postgres for the Aurelius examples.

Part of the template **spine**.

## Services

| Service  | Image                           | Host port                 |
| -------- | ------------------------------- | ------------------------- |
| postgres | `dhi.io/postgres:18-alpine3.23` | `${DATABASE_PORT}` (5432) |

- Database: `aurelius`, user/password `postgres` (dev defaults in `.env`),
  `scram-sha-256` authentication
- Attached to the `aurelius-dev-postgres-network` Docker network, which the FastAPI
  example and the JDBC sink connector join

## Running

```bash
nx serve aurelius-dev-postgres   # docker compose up (foreground)
nx up aurelius-dev-postgres      # detached, waits for healthy
```

The FastAPI example's `serve` target starts this project automatically via
`dependsOn`. The `Entity` table is created by the application at startup in
development — there are no migration files here.
