# aurelius-kafka

Python library wrapping Confluent Kafka for Aurelius services: idempotent topic
management, a batch-friendly producer wrapper, Schema Registry header helpers, and
MSK IAM authentication.

Part of the optional **Kafka streaming slice** — remove this library together
with the rest of that slice.

## API

- `KafkaAdminClient` — admin client with idempotent `create_topics()`
- `KafkaProducer` — producer wrapper with a `batch()` helper
- `build_schema_registry_header()` — Schema Registry wire-format header framing
- `msk.MSKOAuthTokenProvider` — SASL/OAUTHBEARER token provider for AWS MSK IAM

## Dependencies

- `confluent-kafka` (Avro serialisation via `avro` / `pydantic-avro` in callers)
- `aurelius-sdk` (shared utilities)

## Usage

```python
from aurelius_kafka import KafkaProducer, build_schema_registry_header
```

## Testing

```bash
uv run pytest libs/python/aurelius-kafka/tests
```
