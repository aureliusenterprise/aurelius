# aurelius-aws-lambda

Pydantic models for AWS Lambda MSK/Kafka event payloads. This file covers
wiring specific to this lib; workspace-wide rules live in the root `AGENTS.md`
and the Python lib recipe in `libs/python/AGENTS.md`.

## Layout

- `aurelius_aws_lambda/` — `AWSLambdaKafkaEvent`, `AWSLambdaKafkaRecord`,
  `testing.encode_headers()`
- No `tests/` directory, so no Nx `test` target is generated — behaviour is
  covered by `apps/aurelius-aws-lambda-example` unit tests.

## Wiring Checklist

- Part of the AWS Lambda slice: consumed only by
  `apps/aurelius-aws-lambda-example`; registered in root `pyproject.toml`.
- Deliberately pydantic-only (no AWS SDK) — keep it that way so handlers can
  parse events without pulling in boto3.
- `testing.encode_headers()` must match how AWS actually delivers headers
  (base64, wire format) — the app's unit tests rely on that fidelity.

## Commands

```bash
uv run pyright libs/python/aurelius-aws-lambda
```

## Conventions

- Model the AWS event envelope exactly as documented by AWS; when MSK event
  source behaviour changes, update the models and the app's fixtures together.

## Removal

Part of the AWS Lambda slice. Removing it means dropping the dep from
`aurelius-aws-lambda-example` — usually done as part of removing the whole
slice per the root `AGENTS.md` module map.
