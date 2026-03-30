import http.client
from uuid import UUID

import pytest
from aurelius_aws_lambda.testing import Headers, generate_payload
from aurelius_example import Entity
from confluent_kafka import Consumer
from confluent_kafka._types import HeadersType
from confluent_kafka.serialization import (
    Deserializer,
    MessageField,
    SerializationContext,
    Serializer,
)
from timeout_decorator import timeout


@timeout(30)
def consume_message(consumer: Consumer, topic: str) -> tuple[HeadersType | None, bytes | None, bytes | None]:
    """Consume a message from the Kafka topic."""
    consumer.subscribe([topic])

    while not (msg := consumer.poll(timeout=1)):
        continue

    consumer.unsubscribe()

    if msg.error():
        message = f"Error consuming message: {msg.error()}"
        raise RuntimeError(message)

    return msg.headers(), msg.key(), msg.value()


def serialize(
    key: UUID | None,
    value: Entity | None,
    topic: str,
    key_serializer: Serializer,
    value_serializer: Serializer,
) -> tuple[Headers | None, bytes | None, bytes | None]:
    """Serialize the key and value for sending to Kafka."""
    headers = []

    serialized_key: bytes | None = (
        key_serializer(
            str(key),
            SerializationContext(
                field=MessageField.KEY,
                topic=topic,
                headers=headers,
            ),
        )
        if key is not None
        else None
    )

    serialized_value: bytes | None = (
        value_serializer(
            value.model_dump(mode="json"),
            SerializationContext(
                field=MessageField.VALUE,
                topic=topic,
                headers=headers,
            ),
        )
        if value is not None
        else None
    )

    return headers, serialized_key, serialized_value


@pytest.mark.parametrize(
    ("entity", "value_serializer_name"),
    [
        (Entity(), "value_serializer_with_header_schema_id"),
        (Entity(), "value_serializer_with_prefix_schema_id"),
        (Entity(name="Hello World", description="This is a test"), "value_serializer_with_header_schema_id"),
        (Entity(name="Hello World", description="This is a test"), "value_serializer_with_prefix_schema_id"),
    ],
)
def test__aurelius_aws_lambda_example(
    connection: http.client.HTTPConnection,
    consumer: Consumer,
    entity: Entity,
    kafka_topic: str,
    key_deserializer: Deserializer,
    key_serializer: Serializer,
    request: pytest.FixtureRequest,
    value_deserializer: Deserializer,
    value_serializer_name: str,
) -> None:
    """
    Test the Aurelius AWS Lambda example by sending an entity to the Lambda function and consuming it from Kafka.

    Asserts:
        - The HTTP response status is 200.
        - The consumed message key matches the entity's GUID.
        - The consumed message value matches the original entity.
    """
    value_serializer = request.getfixturevalue(value_serializer_name)

    payload = generate_payload(
        kafka_topic,
        serialize(
            key=entity.guid,
            value=entity,
            topic=kafka_topic,
            key_serializer=key_serializer,
            value_serializer=value_serializer,
        ),
    )

    connection.request(
        "POST",
        "/2015-03-31/functions/function/invocations",
        payload,
    )

    response = connection.getresponse()

    assert response.status == 200

    headers, key, value = consume_message(consumer, kafka_topic)

    deserialized_key = key_deserializer(
        key,
        SerializationContext(
            field=MessageField.KEY,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    assert entity.guid == UUID(deserialized_key)

    deserialized_value = value_deserializer(
        value,
        SerializationContext(
            field=MessageField.VALUE,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    assert deserialized_value is not None
    assert entity == Entity.model_validate(deserialized_value)
