# aurelius-aws-lambda

Typed pydantic models for AWS Lambda Kafka event payloads (MSK event source), so
Lambda handlers can parse `event` instead of hand-decoding dictionaries.

Part of the optional **AWS Lambda slice** — remove this library together with
the rest of that slice.

## API

- `AWSLambdaKafkaEvent` — the full MSK/Kafka Lambda event envelope
- `AWSLambdaKafkaRecord` — a single record; decodes base64 payloads and byte
  headers into usable values
- `testing.encode_headers()` — build wire-format headers the way AWS delivers them
  (used in unit tests)

## Dependencies

- `pydantic` only — no AWS SDK required just to parse events

## Usage

```python
from aurelius_aws_lambda import AWSLambdaKafkaEvent

event = AWSLambdaKafkaEvent.model_validate(raw_event)
for record in event.records["topic-0"]:
    ...
```

> [!NOTE]
> This library has no `tests/` directory, so no `test` target is generated for it.
