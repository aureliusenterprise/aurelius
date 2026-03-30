import base64
import json
from datetime import UTC, datetime

type Headers = list[tuple[str, str | bytes | None]]
type EncodedHeaders = list[dict[str, list[int]]]


def encode_headers(headers: Headers) -> EncodedHeaders | None:
    """
    Encode headers to AWS Lambda format (list of byte values).

    This encoding is compatible with how AWS Lambda expects Kafka record headers to be formatted, where each header
    value is represented as a list of byte values.

    Args:
        headers(Headers): A list of tuples containing header key-value pairs.

    Returns:
        EncodedHeaders | None: A list of dictionaries with header keys and byte value lists.
    """
    encoded = []

    for header in headers:
        if header is None:
            continue

        key, value = header

        if isinstance(value, bytes):
            byte_values = list(value)
        elif value is not None:
            byte_values = list(str(value).encode("utf-8"))
        else:
            continue

        encoded.append({key: byte_values})

    return encoded


def generate_payload(topic: str, *records: tuple[Headers | None, bytes | None, bytes | None]) -> str:
    """Generate a test payload compatible with the Kafka event structure expected by AWS Lambda."""
    payload = [
        {
            "headers": encode_headers(headers) if headers is not None else [],
            "key": base64.b64encode(key).decode() if key is not None else None,
            "offset": index,
            "partition": 0,
            "timestamp": datetime.now(tz=UTC).timestamp(),
            "timestampType": "CREATE_TIME",
            "topic": topic,
            "value": base64.b64encode(value).decode() if value is not None else None,
        }
        for index, (headers, key, value) in enumerate(records)
    ]

    return json.dumps(
        {
            "bootstrapServers": "test",
            "eventSource": "aws:kafka",
            "eventSourceArn": "test",
            "records": {
                f"{topic}-0": payload,
            },
        },
    )
