import base64
import json
from datetime import UTC, datetime


def generate_payload(topic: str, *records: tuple[bytes | None, bytes | None]) -> str:
    """Generate a test payload."""
    payload = [
        {
            "headers": [],
            "key": base64.b64encode(key).decode() if key is not None else None,
            "offset": index,
            "partition": 0,
            "timestamp": datetime.now(tz=UTC).timestamp(),
            "timestampType": "CREATE_TIME",
            "topic": topic,
            "value": base64.b64encode(value).decode() if value is not None else None,
        }
        for index, (key, value) in enumerate(records)
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
