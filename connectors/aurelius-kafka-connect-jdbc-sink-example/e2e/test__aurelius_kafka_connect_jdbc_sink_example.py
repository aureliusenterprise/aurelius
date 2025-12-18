from typing import TYPE_CHECKING

import pytest
from aurelius_example import Entity
from tenacity import retry, stop_after_attempt, wait_fixed

if TYPE_CHECKING:
    from uuid import UUID

    from aurelius_kafka import KafkaProducer
    from confluent_kafka.serialization import Serializer
    from sqlmodel import Session


def produce_message(
    entity: Entity,
    kafka_producer: KafkaProducer,
    kafka_topic: str,
    key_serializer: Serializer,
    value_serializer: Serializer,
) -> None:
    """Produce a message to the given Kafka topic."""
    key = key_serializer(str(entity.guid))
    value = value_serializer(entity.model_dump(mode="json"))

    kafka_producer.produce(
        topic=kafka_topic,
        message=(key, value),
    )


def produce_tombstone_message(
    guid: UUID,
    kafka_producer: KafkaProducer,
    kafka_topic: str,
    key_serializer: Serializer,
) -> None:
    """Produce a tombstone message (null value) to the given Kafka topic."""
    key = key_serializer(str(guid))

    kafka_producer.produce(
        topic=kafka_topic,
        message=(key, None),
    )


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def assert_entity_in_database(
    expected: Entity,
    session: Session,
) -> None:
    """Assert that the entity exists in the database."""
    actual = session.get(Entity, expected.guid)
    assert actual == expected, f"Expected {expected} but got {actual}"


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def assert_entity_not_in_database(
    primary_key: UUID,
    session: Session,
) -> None:
    """Assert that the entity does not exist in the database."""
    actual = session.get(Entity, primary_key)
    assert actual is None, f"Expected {primary_key} to be deleted but got {actual}"


@pytest.mark.parametrize(
    "expected",
    [
        Entity(),
        Entity(name="Hello World", description="This is a test"),
    ],
)
def test__aurelius_kafka_connect_jdbc_sink_example_handles_messages(  # noqa: PLR0913
    expected: Entity,
    kafka_producer: KafkaProducer,
    kafka_topic: str,
    key_serializer: Serializer,
    session: Session,
    value_serializer: Serializer,
) -> None:
    """
    Test that messages are correctly processed by the Kafka Connect JDBC Sink.

    Asserts:
        - The entity retrieved from the database matches the expected entity.
    """
    produce_message(
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
        value_serializer=value_serializer,
        entity=expected,
    )

    assert_entity_in_database(expected=expected, session=session)


def test__aurelius_kafka_connect_jdbc_sink_example_handles_tombstone_messages(
    kafka_producer: KafkaProducer,
    kafka_topic: str,
    key_serializer: Serializer,
    session: Session,
    value_serializer: Serializer,
) -> None:
    """
    Test that tombstone messages are correctly processed by the Kafka Connect JDBC Sink.

    First, produce a message to create the entity, then produce a tombstone message to delete it.

    Asserts:
        - The entity is deleted from the database.
    """
    entity = Entity(name="To Be Deleted")

    produce_message(
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
        value_serializer=value_serializer,
        entity=entity,
    )

    assert_entity_in_database(expected=entity, session=session)

    produce_tombstone_message(
        guid=entity.guid,
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
    )

    assert_entity_not_in_database(primary_key=entity.guid, session=session)
