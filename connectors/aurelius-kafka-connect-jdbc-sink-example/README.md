# aurelius-kafka-connect-jdbc-sink-example

Example Kafka Connect deployment: a standalone JDBC sink worker (Debezium's
`JdbcSinkConnector`) writing Avro `Entity` records from `example.entity` into the
development Postgres database, with a dead-letter topic for failures.

Part of the optional **Kafka streaming slice** — remove this project together
with the rest of that slice.

## How it works

- `docker-compose.yaml` runs a single `kafka-connect` service that joins the
  external `aurelius-dev-kafka-network` and `aurelius-dev-postgres-network`
  (start `aurelius-dev-kafka` and `aurelius-dev-postgres` first).
- `workers/worker.properties` — worker config; environment values are injected via
  the `EnvVarConfigProvider` (`${env:VAR}` placeholders).
- `workers/connector.properties` — the sink connector: `insert.mode=upsert` on the
  record key (`guid`), `delete.enabled=true`, `HoistField$Key` + `Flatten$Value`
  transforms, Avro converter against the Schema Registry, and a DLQ on
  `example.entity-dlq`.
- The REST API is exposed on port 8083.

## Image

The multi-stage `Dockerfile` builds on `confluentinc/cp-kafka-connect:8.2.0`
(installing the Avro converter 8.2.0 and Debezium JDBC sink 3.5.1.Final) and runs
on the hardened `dhi.io/kafka:4.3-debian13` base.

## Running

```bash
nx serve aurelius-kafka-connect-jdbc-sink-example
```

The compose file starts `connect-standalone.sh` with the worker and connector
properties mounted in. Verify with:

```bash
curl localhost:8083/connectors   # lists the registered sink connector
```
