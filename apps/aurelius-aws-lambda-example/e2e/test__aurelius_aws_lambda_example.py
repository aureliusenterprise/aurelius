import http.client
from uuid import UUID

import pytest
from aurelius_aws_lambda.testing import generate_payload
from aurelius_example import Entity
from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from timeout_decorator import timeout


@timeout(10)
def consume_message(consumer: Consumer, topic: str) -> tuple[bytes | None, bytes | None]:
    """Consume a message from the Kafka topic."""
    consumer.subscribe([topic])

    while not (msg := consumer.poll(timeout=1)):
        continue

    consumer.unsubscribe()

    if msg.error():
        message = f"Error consuming message: {msg.error()}"
        raise RuntimeError(message)

    return msg.key(), msg.value()


@pytest.mark.parametrize(
    "entity",
    [
        Entity(),
        Entity(name="Hello World", description="This is a test"),
    ],
)
def test__aurelius_aws_lambda_example(  # noqa: PLR0913
    connection: http.client.HTTPConnection,
    consumer: Consumer,
    entity: Entity,
    kafka_topic: str,
    key_deserializer: StringDeserializer,
    key_serializer: StringSerializer,
    value_deserializer: AvroDeserializer,
    value_serializer: AvroSerializer,
) -> None:
    """
    Test the Aurelius AWS Lambda example by sending an entity to the Lambda function and consuming it from Kafka.

    Asserts:
        - The HTTP response status is 200.
        - The consumed message key matches the entity's GUID.
        - The consumed message value matches the original entity.
    """
    payload = generate_payload(
        kafka_topic,
        (
            key_serializer(str(entity.guid)),
            value_serializer(entity.model_dump()),
        ),
    )

    connection.request(
        "POST",
        "/2015-03-31/functions/function/invocations",
        payload,
    )

    response = connection.getresponse()

    assert response.status == 200

    key, value = consume_message(consumer, kafka_topic)

    assert entity.guid == UUID(key_deserializer(key))
    assert value is not None
    assert entity == Entity.model_validate(value_deserializer(value))
