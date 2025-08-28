import json
from typing import Generator

import pytest
from confluent_kafka import Consumer, Producer, TopicCollection
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import Schema, SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
from m4i_atlas_core import get_entity_by_qualified_name
from m4i_data_dictionary_io.sources.kafka.atlas import (
    build_collection,
    build_dataset,
    build_field,
    build_system,
)
from m4i_data_dictionary_io.sources.kafka.create_from_kafka import (
    create_from_kafka,
    discover_cluster,
)
from m4i_data_dictionary_io.testing.models import Envelope, Message
from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential,
)


@pytest.mark.asyncio
async def test__discover_cluster_with_empty_cluster(
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with no topics."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def kafka_topic(
    kafka_admin_client: AdminClient,
    request: pytest.FixtureRequest,
) -> Generator[str, None, None]:
    """Fixture to create a Kafka topic for testing."""
    topic_name = request.node.name

    new_topics = kafka_admin_client.create_topics(
        [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    )

    for future in new_topics.values():
        future.result()

    # Ensure that the topic is discoverable via the admin client
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            descriptions = kafka_admin_client.describe_topics(
                TopicCollection([topic_name])
            )

            for future in descriptions.values():
                future.result()

    yield topic_name

    kafka_admin_client.delete_topics([topic_name])


@pytest.mark.asyncio
async def test__discover_cluster_with_topic(
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    kafka_topic: str,
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

    expected_dataset = build_dataset(
        topic=kafka_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def avro_name_strategy_topic(
    kafka_topic: str,
    schema_registry_client: SchemaRegistryClient,
) -> str:
    """Fixture to create a Kafka topic with an Avro schema using the topic name strategy."""
    schema = Schema(
        schema_str=json.dumps(Envelope.avro_schema()),
        schema_type="AVRO",
    )

    schema_registry_client.register_schema(
        subject_name=f"{kafka_topic}-value",
        schema=schema,
    )

    return kafka_topic


@pytest.mark.asyncio
async def test__discover_cluster_with_avro_schema_using_topic_name_strategy(
    avro_name_strategy_topic: str,
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic with an Avro schema using the topic name strategy."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=avro_name_strategy_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    message_field = build_field(
        name="message",
        dataset_qualified_name=expected_dataset.qualified_name,
        definition="The message contained in the envelope",
        type_name="Message",
    )

    expected_fields = [
        message_field,
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The content of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The topic of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The version of the message",
            parent_field=message_field.qualified_name,
            type_name="long",
        ),
        build_field(
            name="timestamp",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The timestamp of the message",
            type_name="null | long",
        ),
    ]

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
            *expected_fields,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def json_schema_name_strategy_topic(
    kafka_topic: str,
    schema_registry_client: SchemaRegistryClient,
) -> str:
    """Fixture to create a Kafka topic with a JSON schema using the topic name strategy."""
    schema = Schema(
        schema_str=json.dumps(Envelope.model_json_schema()),
        schema_type="JSON",
    )

    schema_registry_client.register_schema(
        subject_name=f"{kafka_topic}-value",
        schema=schema,
    )

    return kafka_topic


@pytest.mark.asyncio
async def test__discover_cluster_with_json_schema_using_topic_name_strategy(
    json_schema_name_strategy_topic: str,
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
) -> None:
    """Test discovering a cluster with a Kafka topic with a JSON schema using the topic name strategy."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=json_schema_name_strategy_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    message_field = build_field(
        name="message",
        dataset_qualified_name=expected_dataset.qualified_name,
        definition="The message contained in the envelope",
        type_name="Message",
    )

    expected_fields = [
        message_field,
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The content of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The topic of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The version of the message",
            parent_field=message_field.qualified_name,
            type_name="integer",
        ),
        build_field(
            name="timestamp",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The timestamp of the message",
            type_name="string",
        ),
    ]

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
            *expected_fields,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture(scope="module")
def message() -> Envelope:
    """Fixture to create a sample message for testing."""
    message = Message(
        content="Test message content",
        name="test_topic",
        version=1,
    )

    return Envelope(message=message)


@pytest.fixture()
def avro_topic(
    avro_serializer: AvroSerializer,
    kafka_producer: Producer,
    kafka_topic: str,
    message: Envelope,
) -> str:
    """Fixture to create a Kafka topic with an Avro message."""
    # The tests may sometimes start before the schema registry is ready. Retry until it is.
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            value = avro_serializer(
                obj=message.model_dump(),
                ctx=SerializationContext(kafka_topic, MessageField.VALUE),
            )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic


@pytest.mark.asyncio
async def test__discover_cluster_with_topic_and_avro_message(
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

    message_field = build_field(
        name="message",
        dataset_qualified_name=expected_dataset.qualified_name,
        definition="The message contained in the envelope",
        type_name="Message",
    )

    expected_fields = [
        message_field,
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The content of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The topic of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The version of the message",
            parent_field=message_field.qualified_name,
            type_name="long",
        ),
        build_field(
            name="timestamp",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The timestamp of the message",
            type_name="null | long",
        ),
    ]

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
            *expected_fields,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def json_schema_topic(
    json_serializer: JSONSerializer,
    kafka_producer: Producer,
    kafka_topic: str,
    message: Envelope,
) -> str:
    """Fixture to create a Kafka topic that has a JSON message with schema."""
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


@pytest.mark.asyncio
async def test__discover_cluster_with_topic_and_json_schema_message(
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

    message_field = build_field(
        name="message",
        dataset_qualified_name=expected_dataset.qualified_name,
        definition="The message contained in the envelope",
        type_name="Message",
    )

    expected_fields = [
        message_field,
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The content of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The topic of the message",
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The version of the message",
            parent_field=message_field.qualified_name,
            type_name="integer",
        ),
        build_field(
            name="timestamp",
            dataset_qualified_name=expected_dataset.qualified_name,
            definition="The timestamp of the message",
            type_name="string",
        ),
    ]

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
            *expected_fields,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def json_topic(
    kafka_producer: Producer,
    kafka_topic: str,
    message: Envelope,
    string_serializer: StringSerializer,
) -> str:
    """Fixture to create a Kafka topic that has a JSON message without schema."""
    value = string_serializer(
        obj=message.model_dump_json(),
        ctx=SerializationContext(kafka_topic, MessageField.VALUE),
    )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic

@pytest.mark.asyncio
async def test__discover_cluster_with_topic_and_json_message(
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

    message_field = build_field(
        name="message",
        dataset_qualified_name=expected_dataset.qualified_name,
        type_name="object",
    )

    expected_fields = [
        message_field,
        build_field(
            name="content",
            dataset_qualified_name=expected_dataset.qualified_name,
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="name",
            dataset_qualified_name=expected_dataset.qualified_name,
            parent_field=message_field.qualified_name,
            type_name="string",
        ),
        build_field(
            name="version",
            dataset_qualified_name=expected_dataset.qualified_name,
            parent_field=message_field.qualified_name,
            type_name="integer",
        ),
        build_field(
            name="timestamp",
            dataset_qualified_name=expected_dataset.qualified_name,
            type_name="string",
        ),
    ]

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
            *expected_fields,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"


@pytest.fixture()
def string_topic(
    kafka_producer: Producer,
    kafka_topic: str,
    string_serializer: StringSerializer,
) -> str:
    """Fixture to create a Kafka topic that has a string message without schema."""
    value = string_serializer(
        obj="Hello, Kafka!",
        ctx=SerializationContext(kafka_topic, MessageField.VALUE),
    )

    kafka_producer.produce(topic=kafka_topic, value=value)
    kafka_producer.poll(0)
    kafka_producer.flush()

    return kafka_topic

@pytest.mark.asyncio
async def test__discover_cluster_with_topic_and_string_message(
    kafka_admin_client: AdminClient,
    kafka_cluster_id: str,
    kafka_consumer: Consumer,
    schema_registry_client: SchemaRegistryClient,
    string_topic: str,
) -> None:
    """Test discovering a cluster with a Kafka topic that has a string message without schema."""
    expected_system = build_system(
        name="kafka_system",
    )

    expected_collection = build_collection(
        name=kafka_cluster_id,
        system_qualified_name=expected_system.qualified_name,
    )

    expected_dataset = build_dataset(
        topic=string_topic,
        collection_qualified_name=expected_collection.qualified_name,
    )

    await create_from_kafka(
        admin_client=kafka_admin_client,
        consumer=kafka_consumer,
        schema_registry_client=schema_registry_client,
    )

    expected = [
        entity.convert_to_atlas()
        for entity in [
            expected_system,
            expected_collection,
            expected_dataset,
        ]
    ]

    for entity in expected:
        # Atlas may not have the entity immediately after creation
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=1, min=2, max=10),
        ):
            with attempt:
                actual = await get_entity_by_qualified_name(
                    entity.attributes.qualified_name,
                    entity.type_name,
                )

                assert (
                    actual is not None
                ), f"Entity {entity.attributes.qualified_name} not found"
