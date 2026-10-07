# aurelius-dev-observability

Local development telemetry stack (OTel Collector, Prometheus, Loki, Tempo,
Grafana). This file covers wiring specific to this project; workspace-wide
rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — the five services, all on
  `aurelius-dev-observability-network`
- `config/` — collector pipelines and Prometheus/Loki/Tempo configs
- `scripts/init-grafana.sh` — provisions Grafana datasources on first start

## Wiring Checklist

- Targets are purely inferred from the compose file (`project.json` has none) —
  add compose-level config there, not in `project.json`.
- Everything exports to the **collector** (4317 gRPC / 4318 HTTP), never
  directly to a backend; new instrumented projects follow the same pattern.
- Consumers started via `nx serve`: the FastAPI example (OTLP), Keycloak
  (`implicitDependencies` here), and the frontend (via its `/otel` dev proxy to
  `:4318`).
- Containers run as unprivileged user `65532` — keep bind-mounted config
  readable by that uid.

## Commands

```bash
nx serve aurelius-dev-observability   # Grafana on http://localhost:3000
```

## Conventions

- Add metrics/traces pipelines in `config/` and reload by restarting the
  collector service rather than editing compose env vars.

## Removal

Part of the spine (workflow reference architecture). Removing it means dropping
the OTLP export wiring from the FastAPI example, Keycloak, and the frontend's
`/otel` proxy and `aurelius-observability` usage.
