# aurelius-observability

Browser OpenTelemetry providers and interceptors for Angular apps. This file
covers wiring specific to this lib; workspace-wide rules live in the root
`AGENTS.md` and the Angular lib recipe in `libs/angular/AGENTS.md`.

## Layout

- `src/lib/` — `provideAureliusOpenTelemetry()`, the tracer injection tokens, and
  `aureliusOpenTelemetryHttpInterceptor`; `src/index.ts` is the public API
- `.spec.ts` files colocated with source

## Wiring Checklist

- `tsconfig.base.json` — `aurelius-observability` path alias used by the frontend.
- Consumed in `apps/aurelius-frontend-example` `app.config.ts`; the exporter is
  chosen by the **app**, not here (the lib defaults to `ConsoleSpanExporter`).
- Dev trace export goes through the frontend's `/otel` proxy
  (`proxy.conf.json` → collector `:4318`) — no collector host config in the lib.
- `package.json` — peer deps pin the OpenTelemetry SDK majors; bump them together
  with the app's direct `@opentelemetry/*` dependencies.

## Commands

```bash
nx test aurelius-observability -c ci   # Vitest unit tests
nx build aurelius-observability        # ng-packagr-lite package build
```

## Conventions

- The lib must stay exporter-agnostic: accept an exporter/options, never import a
  concrete exporter into the public API.
- The interceptor must propagate W3C `traceparent` and set span status from the
  HTTP response — keep both behaviours covered by tests.
- Service name defaults (`aurelius-frontend`) are overridable via options; don't
  hard-code app identity deeper in the lib.

## Removal

Part of the spine. Removing it means removing the `aurelius-observability` alias,
the `provideAureliusOpenTelemetry()` call and interceptor registration in the
frontend, its `/otel` proxy entry, and its `mkdocs.yaml` entries.
