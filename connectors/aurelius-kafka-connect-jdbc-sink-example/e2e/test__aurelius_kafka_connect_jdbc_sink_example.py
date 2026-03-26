from uuid import UUID

import pytest
from aurelius_example import Entity
from confluent_kafka import Producer
from confluent_kafka.serialization import MessageField, SerializationContext, Serializer
from sqlmodel import Session
from tenacity import retry, stop_after_attempt, wait_fixed


def produce_message(
    entity: Entity | None,
    guid: UUID,
    kafka_producer: Producer,
    kafka_topic: str,
    key_serializer: Serializer,
    value_serializer: Serializer,
) -> None:
    """Produce a message to the Kafka topic."""
    headers = {}

    key = key_serializer(
        str(guid),
        SerializationContext(
            field=MessageField.KEY,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    value = value_serializer(
        entity.model_dump(mode="json") if entity else None,
        SerializationContext(
            field=MessageField.VALUE,
            headers=headers,
            topic=kafka_topic,
        ),
    )

    kafka_producer.produce(
        topic=kafka_topic,
        key=key,
        value=value,
        headers=headers,
    )

    kafka_producer.flush()


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
    ("entity", "value_serializer_name"),
    [
        (Entity(), "value_serializer_with_header_schema_id"),
        (Entity(), "value_serializer_with_prefix_schema_id"),
        (Entity(name="Hello World", description="This is a test"), "value_serializer_with_header_schema_id"),
        (Entity(name="Hello World", description="This is a test"), "value_serializer_with_prefix_schema_id"),
    ],
)
def test__aurelius_kafka_connect_jdbc_sink_example_handles_messages(
    entity: Entity,
    kafka_producer: Producer,
    kafka_topic: str,
    key_serializer: Serializer,
    value_serializer_name: str,
    request: pytest.FixtureRequest,
    session: Session,
) -> None:
    """
    Test that messages are correctly processed by the Kafka Connect JDBC Sink.

    Asserts:
        - The entity retrieved from the database matches the expected entity.
    """
    value_serializer: Serializer = request.getfixturevalue(value_serializer_name)

    produce_message(
        entity=entity,
        guid=entity.guid,
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
        value_serializer=value_serializer,
    )

    assert_entity_in_database(expected=entity, session=session)


@pytest.mark.parametrize(
    ("entity", "value_serializer_name"),
    [
        (Entity(name="To Be Deleted"), "value_serializer_with_header_schema_id"),
        (Entity(name="To Be Deleted"), "value_serializer_with_prefix_schema_id"),
    ],
)
def test__aurelius_kafka_connect_jdbc_sink_example_handles_tombstone_messages(
    entity: Entity,
    kafka_producer: Producer,
    kafka_topic: str,
    key_serializer: Serializer,
    value_serializer_name: str,
    request: pytest.FixtureRequest,
    session: Session,
) -> None:
    """
    Test that tombstone messages are correctly processed by the Kafka Connect JDBC Sink.

    First, produce a message to create the entity, then produce a tombstone message to delete it.

    Asserts:
        - The entity is deleted from the database.
    """
    value_serializer: Serializer = request.getfixturevalue(value_serializer_name)

    produce_message(
        entity=entity,
        guid=entity.guid,
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
        value_serializer=value_serializer,
    )

    assert_entity_in_database(expected=entity, session=session)

    produce_message(
        entity=None,
        guid=entity.guid,
        kafka_producer=kafka_producer,
        kafka_topic=kafka_topic,
        key_serializer=key_serializer,
        value_serializer=value_serializer,
    )

    assert_entity_not_in_database(primary_key=entity.guid, session=session)
