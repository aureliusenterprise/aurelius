# aurelius-dev-kafka

Local development Kafka cluster: a KRaft-mode broker, Confluent Schema Registry,
and a browser-based Kafka UI, wired onto a shared Docker network for the other
Kafka-slice projects.

Part of the optional **Kafka streaming slice** — remove this project together
with the rest of that slice.

## Services

| Service         | Image                       | Host port | Notes                      |
| --------------- | --------------------------- | --------- | -------------------------- |
| Kafka broker    | `dhi.io/kafka:4.3-debian13` | 9092      | KRaft mode, no ZooKeeper   |
| Schema Registry | `cp-schema-registry:8.2.1`  | 8081      | Avro, `RecordNameStrategy` |
| Kafka UI        | `kafbat/kafka-ui`           | 8082      | Browse topics, schemas     |

Inside the `aurelius-dev-kafka-network` Docker network, containers reach the broker
at `broker:9094` (host apps use `localhost:9092`; the controller runs on 9093).

## Configuration

- `server.properties` is bind-mounted (replication factor 1, 3 default partitions)
- The compose project exposes the `aurelius-dev-kafka-network` network, which other
  projects (e.g. the JDBC sink connector) attach to from their own compose files

## Running

```bash
nx serve aurelius-dev-kafka   # docker compose up (foreground)
nx up aurelius-dev-kafka      # detached, waits for healthy
```

Other projects (Java producer, Node-RED, Lambda E2E, JDBC sink) declare a
`dependsOn` on this project's `serve`/`up` target, so `nx serve` on them starts
Kafka automatically.
