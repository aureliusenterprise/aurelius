from typing import Generator

import pytest
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
from m4i_data_dictionary_io.sources.kafka.create_from_kafka import (
    build_collection,
    build_dataset,
    build_field,
    build_system,
    discover_cluster,
)
from m4i_data_dictionary_io.testing.message import Message
from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential,
)


def test__discover_cluster_with_empty_cluster(
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with an empty Kafka topic."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected = [expected_system, expected_collection]

    discovered = discover_cluster(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    actual = list(discovered)

    assert expected == actual, f"Expected {expected} but got {actual}"


@pytest.fixture()
def kafka_topic(
    kafka_admin_client: AdminClient,
    request: pytest.FixtureRequest,
) -> Generator[str, None, None]:
    """Fixture to create a Kafka topic for testing."""
    topic_name = request.node.name

    futures = kafka_admin_client.create_topics(
        [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    )

    for future in futures.values():
        if future.exception():
            raise RuntimeError(f"Failed to create topic {topic_name}")
        future.result()

    yield topic_name

    kafka_admin_client.delete_topics([topic_name])


def test__discover_cluster_with_topic(
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    kafka_topic: str,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=kafka_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    expected = [expected_system, expected_collection, expected_dataset]

    discovered = discover_cluster(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    actual = list(discovered)

    assert expected == actual, f"Expected {expected} but got {actual}"


@pytest.fixture(scope="module")
def message() -> Message:
    """Fixture to create a Message instance for testing."""
    return Message(
        content="Test message content",
        name="test_topic",
        version=1,
    )


@pytest.fixture()
def avro_topic(
    avro_serializer: AvroSerializer,
    kafka_producer: Producer,
    kafka_topic: str,
    message: Message,
) -> str:
    """Fixture to create a Kafka topic with an Avro message."""
    # The tests may sometimes start before the schema registry is ready. Retry until it is.
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            value = avro_serializer(
                obj=message.model_dump(mode="json"),
                ctx=SerializationContext(kafka_topic, MessageField.VALUE),
            )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic


def test__discover_cluster_with_topic_and_avro_message(
    avro_topic: str,
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic that has an Avro message."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=avro_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    expected_fields = [
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="long",
        ),
    ]

    expected = [
        expected_system,
        expected_collection,
        expected_dataset,
        *expected_fields,
    ]

    discovered = discover_cluster(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    actual = list(discovered)

    assert expected == actual, f"Expected {expected} but got {actual}"


@pytest.fixture()
def json_schema_topic(
    json_serializer: JSONSerializer,
    kafka_producer: Producer,
    kafka_topic: str,
    message: Message,
) -> str:
    """Fixture to create a Kafka topic with a JSON message with schema."""
    # The tests may sometimes start before the schema registry is ready. Retry until it is.
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            value = json_serializer(
                obj=message.model_dump(mode="json"),
                ctx=SerializationContext(kafka_topic, MessageField.VALUE),
            )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic


def test__discover_cluster_with_topic_and_json_schema_message(
    json_schema_topic: str,
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic that has a JSON message with schema."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=json_schema_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    expected_fields = [
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="integer",
        ),
    ]

    expected = [
        expected_system,
        expected_collection,
        expected_dataset,
        *expected_fields,
    ]

    discovered = discover_cluster(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    actual = list(discovered)

    assert expected == actual, f"Expected {expected} but got {actual}"


@pytest.fixture()
def json_topic(
    kafka_producer: Producer,
    kafka_topic: str,
    message: Message,
    string_serializer: StringSerializer,
) -> str:
    """Fixture to create a Kafka topic that has a JSON message without schema."""
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            value = string_serializer(
                obj=message.model_dump_json(),
                ctx=SerializationContext(kafka_topic, MessageField.VALUE),
            )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic


def test__discover_cluster_with_topic_and_json_message(
    json_topic: str,
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic that has a JSON message without schema."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=json_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    expected_fields = [
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="integer",
        ),
    ]

    expected = [
        expected_system,
        expected_collection,
        expected_dataset,
        *expected_fields,
    ]

    discovered = discover_cluster(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    actual = list(discovered)

    assert expected == actual, f"Expected {expected} but got {actual}"
