# aurelius-dev-kafka

Local development Kafka cluster. This file covers wiring specific to this
project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — broker (KRaft), Schema Registry, Kafka UI
- `server.properties` — bind-mounted broker config (RF 1, 3 partitions)
- `.env` / `.env.enc` — SOPS-encrypted dev settings

## Wiring Checklist

- Part of the Kafka streaming slice (see root `AGENTS.md` module map).
- Exposes the external Docker network `aurelius-dev-kafka-network`; the Java
  producer, Node-RED, JDBC sink connector, and Lambda E2E attach to it and
  reach the broker at `broker:9094` (host apps use `localhost:9092`).
- Those projects declare `dependsOn` on this project's `serve`/`up` target in
  their `project.json` — new Kafka consumers/producers should do the same.
- Schema Registry uses `RecordNameStrategy`; subject names follow
  `example.entity` from `Entity.avsc`'s namespace.

## Commands

```bash
nx serve aurelius-dev-kafka   # compose up (foreground)
nx up aurelius-dev-kafka      # detached, waits for healthy
nx decrypt aurelius-dev-kafka # SOPS: .env.enc → .env (serve does this for you)
```

## Conventions

- Change broker behaviour via `server.properties`, not compose `environment:`
  overrides, so the config stays reviewable in one file.
- Ports 9092/8081/8082 are part of the workspace contract (apps' `.env` files
  point at them) — coordinate before changing.

## Removal

Removing this project means removing the whole Kafka streaming slice per the
root `AGENTS.md` module map (java-producer, node-red, aurelius-kafka,
aurelius-java-example, the JDBC sink connector, and the Lambda slice's Kafka
event source).
