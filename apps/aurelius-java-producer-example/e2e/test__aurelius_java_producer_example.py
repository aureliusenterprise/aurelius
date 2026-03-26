import unittest.mock
from uuid import UUID

from aurelius_example import Entity
from confluent_kafka import Consumer
from confluent_kafka._types import HeadersType
from confluent_kafka.serialization import Deserializer, MessageField, SerializationContext
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


def test__aurelius_java_producer_example(
    consumer: Consumer,
    kafka_topic: str,
    key_deserializer: Deserializer,
    value_deserializer: Deserializer,
) -> None:
    """
    Test the Aurelius Java Producer example by consuming a message from the Kafka topic and validating its contents.

    Asserts:
        - The consumed message has a key and a value.
        - The value can be deserialized into an Entity object.
    """
    headers, key, value = consume_message(consumer, kafka_topic)

    assert key is not None
    assert value is not None

    deserialized_key = key_deserializer(
        key,
        SerializationContext(
            field=MessageField.KEY,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    deserialized_value = value_deserializer(
        value,
        SerializationContext(
            field=MessageField.VALUE,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    expected = Entity(
        guid=UUID(deserialized_key),
        description=unittest.mock.ANY,
        name=unittest.mock.ANY,
    )

    actual = Entity.model_validate(deserialized_value)

    assert expected == actual
