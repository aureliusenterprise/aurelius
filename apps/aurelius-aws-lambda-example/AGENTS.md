# aurelius-aws-lambda-example

Example Kafka-triggered AWS Lambda (container image). This file covers wiring
specific to this app; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `aurelius_aws_lambda_example/` — the package
    - `handler.py` — `main` plus the `initialize()` warm-start hook (Powertools
      `kafka_consumer`): builds settings, Avro serdes, and the producer
    - `processor.py` — payload decoding and record round-trip
- `e2e/` — pytest suite running the image in the Lambda RIE (port 8080) with its
  own `docker-compose.yaml` (Kafka + Schema Registry)

## Configuration

- Settings are pydantic `BaseSettings`; keys come from `.env` (dev default) and
  `.env.enc` (SOPS). `KAFKA_BOOTSTRAP_SERVERS` and `SCHEMA_REGISTRY_URL` are
  supplied by the e2e compose and by Lambda environment variables in deployment.

## Wiring Checklist

- `project.json` — `implicitDependencies`: `aurelius-aws-lambda`, `aurelius-kafka`,
  `aurelius-example`, `aurelius-dev-kafka`, `aurelius-aws-lambda-base`.
- `Dockerfile` — `FROM ghcr.io/aureliusenterprise/aurelius-aws-lambda-base:${VERSION}`
  and `CMD aurelius_aws_lambda_example.main`. Bumping the base image means
  releasing it first; `nx release` keeps `${VERSION}` in sync.
- `pyproject.toml` — workspace deps via `[tool.uv.sources] workspace = true`.
- `mkdocs.yaml` — API reference page under `docs/api-reference/apps/`.

## Commands

```bash
nx test aurelius-aws-lambda-example -c ci
nx e2e aurelius-aws-lambda-example            # RIE + real Kafka/Schema Registry
nx docker-build aurelius-aws-lambda-example
```

## Conventions

- Parse events with the `aurelius_aws_lambda` models — never hand-decode the event
  dict.
- Build expensive clients (producer, serdes) in `initialize()`, not in `main`.
- Schema framing is header-based with `RecordNameStrategy` — match it in any new
  producer/consumer pair.

## Removal

Part of the optional AWS Lambda slice. Removing this app also removes (or makes
dead): `libs/python/aurelius-aws-lambda`, `docker/aurelius-aws-lambda-base`,
root `pyproject.toml` entries, `mkdocs.yaml` nav, and the slice row in the root
`AGENTS.md` module map.
