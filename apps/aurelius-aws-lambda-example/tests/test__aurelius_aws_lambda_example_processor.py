import json
from base64 import b64encode
from unittest.mock import MagicMock, call
from uuid import UUID

from aurelius_aws_lambda_example.processor import deserialize, process, serialize
from aurelius_example import Entity
from aws_lambda_powertools.utilities.kafka.consumer_records import ConsumerRecordRecords, ConsumerRecords
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext


def test__deserialize_returns_entity_when_value_is_present() -> None:
    """
    Test that deserialize returns an Entity instance when the record value is present.

    Asserts:
        - The deserialized key matches the expected key.
        - The deserialized value is an Entity instance that matches the expected entity.
    """
    expected_key = b"key-1"
    expected_value = Entity(name="example", description="entity")

    record = ConsumerRecordRecords(
        {
            "key": b64encode(expected_key),
            "value": b64encode(expected_value.model_dump_json().encode("utf-8")),
            "headers": [{"x-source": b"lambda"}],
            "topic": "test-topic",
        },
    )

    value_deserializer = MagicMock(return_value=expected_value.model_dump(mode="json"))

    actual_key, actual_value = deserialize(record, value_deserializer=value_deserializer)

    assert actual_key == expected_key
    assert actual_value == expected_value


def test__deserialize_returns_none_entity_when_value_is_empty() -> None:
    """
    Test that deserialize returns None for the entity when the record value is empty.

    Asserts:
        - The deserialized key matches the expected key.
        - The deserialized value is None when the record value is empty.
    """
    expected_key = b"key-2"
    expected_value = None

    record = ConsumerRecordRecords(
        {
            "key": b64encode(expected_key),
            "value": None,
            "headers": [{"x-source": b"lambda"}],
            "topic": "test-topic",
        },
    )

    value_deserializer = MagicMock(return_value=None)

    actual_key, actual_value = deserialize(record, value_deserializer=value_deserializer)

    assert actual_key == expected_key
    assert actual_value == expected_value


def test__serialize_returns_default_headers_and_serialized_value() -> None:
    """
    Test that serialize returns the expected serialized value and default headers when no headers are provided.

    Asserts:
        - The returned headers are an empty list when no headers are provided.
        - The returned serialized value matches the expected serialized value.
    """
    expected_headers = []
    expected_value = b"serialized"

    value_serializer = MagicMock(return_value=expected_value)

    actual_headers, actual_value = serialize(
        value=Entity(name="example", description="entity"),
        topic_name="target-topic",
        value_serializer=value_serializer,
    )

    assert actual_headers == expected_headers
    assert actual_value == expected_value


def test__serialize_uses_provided_headers_and_none_value() -> None:
    """
    Test that serialize uses the provided headers and handles None value correctly.

    Asserts:
        - The returned headers match the provided headers.
        - The returned serialized value matches the expected serialized value.
    """
    expected_headers = [{"x-trace-id": b"abc"}]
    expected_value = b"serialized"

    value_serializer = MagicMock(return_value=expected_value)

    actual_headers, actual_value = serialize(
        value=None,
        topic_name="target-topic",
        headers=expected_headers,  # type: ignore[headers format is valid]
        value_serializer=value_serializer,
    )

    assert actual_headers == expected_headers
    assert actual_value == expected_value


def test__process_deserializes_produces_and_flushes() -> None:
    """
    Test that process deserializes records, produces messages, and flushes the producer.

    Asserts:
        - The producer produces messages with the correct arguments.
        - The producer flushes once after processing all records.
    """
    entity = Entity(
        guid=UUID("835e0c0d-f911-4ec6-8667-60ac75c6cb93"),
        name="example",
        description="entity",
    )

    event = ConsumerRecords(
        {
            "records": {
                "partition": [
                    {
                        "key": b64encode(str(entity.guid).encode("utf-8")),
                        "value": b64encode(entity.model_dump_json().encode("utf-8")),
                        "headers": [{"x-source": b"lambda"}],
                        "topic": "input-topic",
                    },
                    {
                        "key": b64encode(str(entity.guid).encode("utf-8")),
                        "value": None,
                        "headers": [{"x-source": b"lambda"}],
                        "topic": "input-topic",
                    },
                ],
            },
        },
    )

    def value_deserializer(value: bytes | None, _: SerializationContext | None = None) -> dict | None:
        return json.loads(value.decode("utf-8")) if value is not None else None

    def value_serializer(value: dict | None, _: SerializationContext | None = None) -> bytes | None:
        return json.dumps(value).encode("utf-8") if value is not None else None

    producer = MagicMock(spec=Producer)

    process(
        event,
        topic_name="output-topic",
        value_deserializer=value_deserializer,  # type: ignore[callable]
        value_serializer=value_serializer,  # type: ignore[callable]
        producer=producer,
    )

    producer.produce.assert_has_calls(
        [
            call(
                topic="output-topic",
                key=str(entity.guid).encode("utf-8"),
                value=json.dumps(entity.model_dump(mode="json")).encode("utf-8"),
                headers=[],
            ),
            call(
                topic="output-topic",
                key=str(entity.guid).encode("utf-8"),
                value=None,
                headers=[],
            ),
        ],
    )

    producer.flush.assert_called_once_with()
