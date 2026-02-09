import unittest.mock
from uuid import UUID

from aurelius_example import Entity
from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
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


def test__aurelius_node_red_example(
    consumer: Consumer,
    kafka_topic: str,
    key_deserializer: StringDeserializer,
    value_deserializer: AvroDeserializer,
) -> None:
    """
    Test the Aurelius Node-RED example by consuming a message from the Kafka topic and validating its contents.

    Asserts:
        - The consumed message has a key and a value.
        - The value can be deserialized into an Entity object.
    """
    key, value = consume_message(consumer, kafka_topic)

    assert key is not None
    assert value is not None

    deserialized_key = key_deserializer(key)

    expected = Entity(
        guid=UUID(deserialized_key),
        description=unittest.mock.ANY,
        name=unittest.mock.ANY,
    )

    actual = Entity.model_validate(value_deserializer(value))

    assert expected == actual
