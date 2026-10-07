# aurelius-java-producer-example

Example Java 21 console application demonstrating the Aurelius Kafka producer
pattern: it publishes Avro-serialised `Entity` records to a Kafka topic on a fixed
interval, using Confluent's Schema Registry.

Part of the optional **Kafka streaming slice** — remove this project together
with the rest of that slice.

## How it works

- `App.java` — main loop: load config, produce a record every
  `MESSAGE_INTERVAL_MILLIS`, shut down cleanly via a shutdown hook.
- `EntityProducer` — wraps `KafkaProducer<String, Entity>` with a
  `KafkaAvroSerializer` (header schema-id framing, `RecordNameStrategy` naming).
- `AppConfig` — a record populated from environment variables, with a small `.env`
  file loader used by the `run` target.
- The `Entity` Java class is **generated** by the sibling `aurelius-java-example`
  library from the Avro schemas in `schemas/avro/` — never edit it by hand.

## Configuration

| Variable                  | Default                 | Purpose                |
| ------------------------- | ----------------------- | ---------------------- |
| `KAFKA_TOPIC_NAME`        | `example.entity`        | Target topic           |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092`        | Broker address         |
| `SCHEMA_REGISTRY_URL`     | `http://localhost:8081` | Schema Registry        |
| `MESSAGE_INTERVAL_MILLIS` | `10000`                 | Delay between messages |

## Running

```bash
nx serve aurelius-dev-kafka        # start broker + Schema Registry first
nx run aurelius-java-producer-example:run
```

Confluent artifacts come from the Confluent Maven repository declared in
`build.gradle.kts`.

## Testing

```bash
./gradlew :aurelius-java-producer-example:test   # JUnit 5 + JaCoCo coverage
nx e2e aurelius-java-producer-example            # pytest E2E against a real broker
```
