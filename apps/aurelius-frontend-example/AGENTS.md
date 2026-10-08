# aurelius-frontend-example

Example Angular SPA. This file covers wiring specific to this app; workspace-wide
rules live in the root `AGENTS.md`.

## Layout

- `src/app/` — standalone, zoneless components; `app.config.ts` wires providers
  (Keycloak, OpenTelemetry, interceptors); routes in `app.routes.ts`
- `dev/config.json` — runtime Keycloak config, bundled **only** in the development
  build (see `build.configurations.development.assets` in `project.json`)
- `proxy.conf.json` — dev-server proxy: `/api` → backend on 8000 (prefix stripped),
  `/otel` → OTLP collector on 4318
- `e2e/` — pytest + Playwright (chromium, firefox, webkit)

## Configuration

- Keycloak client/realm come from `/config.json`, fetched at bootstrap — never
  hard-code them. Production deployments must serve their own `config.json`.
- The bearer token is attached to `/api/*` requests via `includeBearerTokenInterceptor`.

## Wiring Checklist

- `project.json` — `implicitDependencies` (keycloak, observability, fastapi) and
  the `serve` `dependsOn`; the `development` build config is what includes `dev/`
  assets, so secrets never leak into production bundles.
- `tsconfig.base.json` — add a path alias when consuming a new Angular lib.
- `package.json` — `@aurelius/brand` is a `file:` dependency.
- `Dockerfile` — static nginx (`dhi.io/nginx`, port 8080); keep proxy/otel paths in
  sync when backend or collector routes change.
- `mkdocs.yaml` — user-guide pages referencing this app.

## Commands

```bash
nx serve aurelius-frontend-example        # starts Keycloak + FastAPI first
nx test aurelius-frontend-example -c ci   # never without -c ci (watch mode hangs)
nx e2e aurelius-frontend-example          # builds image, runs Playwright
nx extract-i18n aurelius-frontend-example # refresh translation bundles
nx lint aurelius-frontend-example
```

Offline-safe: `nx test -c ci`, `nx lint`, `extract-i18n`. Needs Docker: `serve`, `e2e`.

## Conventions

- Components stay presentational; data access goes through `aurelius-data-access`,
  shared UI through `aurelius-ui`, styling tokens through `@aurelius/brand`.
- Follow the existing injectable-service pattern in `src/app` for new state.
- New routes need E2E coverage in `e2e/`.

## Removal

This app is part of the spine. If a fork removes it, also remove: its `mkdocs.yaml`
nav entry and CI references. The backend and Keycloak realm client can stay — they
serve other consumers.
