# aurelius-kafka-connect-jdbc-sink-example

Standalone Kafka Connect JDBC sink deployment. This file covers wiring specific
to this project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — single `connect-standalone.sh` worker
- `workers/worker.properties` — worker config, `${env:VAR}` values via
  `EnvVarConfigProvider`
- `workers/connector.properties` — the sink connector definition
- `Dockerfile` — cp-kafka-connect base + Avro converter + Debezium JDBC sink
- `.env` / `.env.enc` — SOPS-encrypted dev settings

## Wiring Checklist

- `project.json` `implicitDependencies`: `aurelius-dev-kafka`,
  `aurelius-dev-postgres`, `aurelius-example`, `aurelius-kafka`.
- Compose joins the external networks `aurelius-dev-kafka-network` and
  `aurelius-dev-postgres-network` — both must be up (`nx up aurelius-dev-kafka
aurelius-dev-postgres`) before `nx serve` here works.
- The connector writes Avro `Entity` records from `example.entity` into the dev
  Postgres with `insert.mode=upsert` on `guid`; transforms
  (`HoistField$Key`, `Flatten$Value`) assume the current `Entity` field set —
  update them when `libs/python/aurelius-example` changes.
- Failures go to the `example.entity-dlq` dead-letter topic.
- REST API on port 8083 is part of the local contract.

## Commands

```bash
nx serve aurelius-kafka-connect-jdbc-sink-example
curl localhost:8083/connectors   # verify the sink is registered
```

## Conventions

- Config changes belong in the `workers/*.properties` files (with `${env:VAR}`
  for anything secret), not in compose `environment:` blocks beyond the
  injections those files reference.
- Converter/plugin versions in the `Dockerfile` must match the dev Kafka
  cluster's Schema Registry version line.

## Removal

Part of the Kafka streaming slice. Removing it is self-contained (its own
compose + image); also drop it from any docs referencing the streaming flow.
