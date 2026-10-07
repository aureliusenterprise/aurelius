# aurelius-dev-keycloak

Local development identity provider. This file covers wiring specific to this
project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — Keycloak plus its private Postgres
- `import/master.json` — realm, clients, and test users, imported on startup
- `.env` / `.env.enc` — SOPS-encrypted dev settings

## Wiring Checklist

- `project.json` `implicitDependencies` on `aurelius-dev-observability`; the
  `serve` target chains `decrypt` → `docker-build` → dependency `serve`, and
  exports OTLP to `otel-collector:4317`.
- Issuer URL `http://keycloak.localhost:8080` must match the auth settings the
  FastAPI example validates and the frontend's `/config.json` advertises —
  change all three together.
- Realms/clients/test users live in `import/master.json`; edit there rather
  than mutating the running container (changes are lost on recreate otherwise).
- The frontend's `serve` target depends on this project's `serve`.

## Commands

```bash
nx serve aurelius-dev-keycloak   # decrypt + build + observability + up
```

## Conventions

- First start takes a couple of minutes to become healthy — that's normal, not
  a hang.
- Keep `import/master.json` idempotent (fixed UUIDs where needed) so re-imports
  don't churn.

## Removal

Part of the spine. Removing it means replacing auth in the FastAPI example and
dropping the Keycloak config/interceptor wiring from the frontend.
