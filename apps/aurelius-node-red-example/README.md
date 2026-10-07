# aurelius-node-red-example

Example Node-RED application demonstrating the Aurelius Kafka producer pattern with
a low-code flow: every 10 seconds it generates an `Entity` message and produces it
to Kafka with Avro serialisation.

Part of the optional **Kafka streaming slice** — remove this project together
with the rest of that slice.

## How it works

- `flows.json` — the exported flow ("Events" tab): inject → UUID generation →
  field population → Kafka producer node (plus a debug node).
- `settings.js` / `settings.prod.js` — Node-RED runtime settings; the production
  variant disables the editor and serves on port 1880.
- Kafka/Avro support comes from the `@oriolrius/node-red-contrib-kafka` and
  `node-red-contrib-uuid` palette nodes.

## Configuration

| Variable                  | Default                                 | Purpose              |
| ------------------------- | --------------------------------------- | -------------------- |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092`                        | Broker address       |
| `KAFKA_TOPIC_NAME`        | `example.entity`                        | Target topic         |
| `SCHEMA_REGISTRY_URL`     | `http://localhost:8081`                 | Schema Registry      |
| `SCHEMA_SUBJECT_NAME`     | `com.aureliusenterprise.example.Entity` | Avro subject         |
| `SCHEMA_SUBJECT_VERSION`  | `latest`                                | Avro subject version |

## Running

```bash
nx serve aurelius-node-red-example
```

Starts `node-red` with this directory as the user directory (the `serve` target
also starts `aurelius-dev-kafka` first). The editor is available on port 1880.

## Testing

```bash
nx e2e aurelius-node-red-example   # pytest E2E against a real broker
```
