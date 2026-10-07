# aurelius-observability

Browser OpenTelemetry setup for Aurelius Angular apps: a tracer provider wired
into Angular's dependency injection, plus an HTTP interceptor that propagates
trace context on outgoing requests.

Part of the template **spine**.

## API

- `provideAureliusOpenTelemetry(options?)` — environment providers registering the
  tracer; defaults to a `ConsoleSpanExporter` and service name `aurelius-frontend`
- `createAureliusWebTracerProvider(options?)` — the raw `WebTracerProvider` if you
  need it outside DI
- `AURELIUS_WEB_TRACER_PROVIDER` / `AURELIUS_TRACER` — injection tokens for the
  provider and a default tracer
- `aureliusOpenTelemetryHttpInterceptor` — functional HTTP interceptor adding W3C
  `traceparent` and `X-Trace-Id` headers and setting span status from the response

## Usage

```ts
// app.config.ts
import { provideAureliusOpenTelemetry } from "aurelius-observability";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

export const appConfig: ApplicationConfig = {
    providers: [
        provideAureliusOpenTelemetry({
            exporter: new OTLPTraceExporter({ url: "/otel/v1/traces" }),
        }),
    ],
};
```

The frontend example exports through its dev proxy (`/otel` → OTLP collector on
port 4318) so no CORS or collector host config is needed in development.
