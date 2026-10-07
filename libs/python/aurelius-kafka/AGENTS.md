# aurelius-kafka

Python Confluent Kafka wrapper (admin client, producer, Schema Registry headers,
MSK IAM auth). This file covers wiring specific to this lib; workspace-wide
rules live in the root `AGENTS.md` and the Python lib recipe in
`libs/python/AGENTS.md`.

## Layout

- `aurelius_kafka/` — `KafkaAdminClient`, `KafkaProducer`,
  `build_schema_registry_header()`, `msk.MSKOAuthTokenProvider`
- `tests/test__*.py` — pytest suite
- Depends on `confluent-kafka` and `aurelius-sdk`

## Wiring Checklist

- Part of the Kafka streaming slice: consumed by `aurelius-fastapi-example` and
  `aurelius-aws-lambda-example`; registered in root `pyproject.toml`.
- Topic names follow the `example.<entity>` convention used by the Schema
  Registry subjects, the Java producer, and the JDBC sink — keep them aligned.
- Avro serialisation itself lives in callers (pydantic-avro on `Entity`); this
  lib only handles transport and framing.

## Commands

```bash
uv run pytest libs/python/aurelius-kafka/tests
uv run pyright libs/python/aurelius-kafka
```

## Conventions

- `create_topics()` must stay idempotent — services call it on every startup.
- MSK IAM support (`msk.py`) is for AWS deployments; local dev uses plaintext
  SASL settings from the app's `.env`. Do not mix the two code paths.

## Removal

Part of the Kafka streaming slice. Removing it means dropping the dep from the
consuming apps and deleting their Kafka wiring — usually done as part of
removing the whole slice per the root `AGENTS.md` module map.
