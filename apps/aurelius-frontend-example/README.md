# aurelius-frontend-example

Example Angular 22 single-page app demonstrating the Aurelius frontend pattern:
a zoneless, standalone-component SPA protected by Keycloak, talking to the FastAPI
backend and exporting browser telemetry through OpenTelemetry.

Part of the template **spine**.

## Features

- The whole app sits behind one Keycloak-guarded root route (`createAuthGuard` with
  login redirect)
- Entity search with debounced queries and pagination, plus an entity editor
- Runtime config: `/config.json` (Keycloak client/realm) is fetched at bootstrap and
  only bundled in the development build (`dev/config.json`)
- `provideAureliusOpenTelemetry()` traces exported via `/otel/v1/traces`;
  bearer-token interceptor attached to `/api/*` calls

## Workspace dependencies

- `aurelius-ui` — presentational Bulma components
- `aurelius-data-access` — typed HTTP + SSE client for the backend
- `aurelius-observability` — browser OpenTelemetry setup
- `@aurelius/brand` (`libs/styles/aurelius-brand`) — SCSS design tokens

## Running

```bash
nx serve aurelius-frontend-example
```

Serves on `http://localhost:4200` with a dev proxy: `/api` → the FastAPI backend on
port 8000 (prefix stripped) and `/otel` → the OTLP collector on port 4318.

## Testing

```bash
nx test aurelius-frontend-example -c ci      # Vitest unit tests
nx e2e aurelius-frontend-example             # Playwright (chromium, firefox, webkit)
nx extract-i18n aurelius-frontend-example    # refresh translation bundles
```

## Deployment

The production Docker image is a static nginx serve (`dhi.io/nginx`, port 8080);
`/config.json` is supplied at deploy time instead of being baked in.
