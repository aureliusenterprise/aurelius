import json
import logging
from typing import Callable, Dict, Generator, List, Union

from confluent_kafka import Consumer, TopicCollection
from confluent_kafka.admin import AdminClient
from confluent_kafka.avro import loads
from confluent_kafka.schema_registry import (
    Schema,
    SchemaRegistryClient,
    SchemaRegistryError,
)
from m4i_data_dictionary_io.entities.json import (
    Collection,
    DataField,
    Dataset,
    System,
    ToAtlasConvertible,
    get_qualified_name,
)
from m4i_data_dictionary_io.functions.create_from_excel import get_ref_and_push

SCHEMA_REGISTRY_MAGIC_BYTE = b"\x00"


def get_cluster_id(admin_client: AdminClient) -> Union[str, None]:
    """Retrieve the cluster ID from the Kafka admin client."""
    future = admin_client.describe_cluster()

    return (
        cluster_metadata.cluster_id if (cluster_metadata := future.result()) else None
    )


def get_external_topic_names(admin_client: AdminClient) -> List[str]:
    """
    Retrieve topic names for the given cluster ID,
    filtering out internal and default topics.
    """
    all_topics = [str(t) for t in admin_client.list_topics().topics.values()]

    futures = admin_client.describe_topics(TopicCollection(all_topics))

    external_topics = [
        topic_name
        for topic_name, future in futures.items()
        if not ((t := future.result()) and t.is_internal)
    ]

    return [
        topic
        for topic in external_topics
        if not topic.startswith("_")
        or topic.endswith(("-offsets", "-status", "-configs"))
    ]


def consume_message(topic: str, consumer: Consumer) -> Union[bytes, None]:
    """Consume a single message from the provided topic."""
    try:
        consumer.subscribe([topic])
        msg = consumer.poll(5)
    finally:
        consumer.unsubscribe()

    if msg is None or msg.error():
        return None

    return msg.value()


def get_message_schema(
    message: bytes,
    schema_registry_client: SchemaRegistryClient,
) -> Union[Schema, None]:
    if not message.startswith(SCHEMA_REGISTRY_MAGIC_BYTE):
        logging.warning("Message is not schema-registered")
        return None

    try:
        schema_id = int.from_bytes(message[1:5], "big")
    except IndexError:
        logging.error("Message is too short to contain a schema ID")
        return None

    try:
        schema = schema_registry_client.get_schema(schema_id)
    except SchemaRegistryError:
        logging.error(f"Failed to retrieve schema with ID {schema_id}")
        return None

    return schema


def build_system(name: str) -> System:
    return System.from_dict(
        {
            "name": name,
            "qualifiedName": get_qualified_name(name),
        }
    )


def build_collection(
    name: str,
    system_qualified_name: str,
) -> Collection:
    return Collection.from_dict(
        {
            "name": name,
            "system": system_qualified_name,
            "qualifiedName": f"{system_qualified_name}--{get_qualified_name(name)}",
        }
    )


def build_dataset(topic: str, collection_qualified_name: str) -> Dataset:
    """Process each topic by creating dataset and field instances."""
    dataset_qualified_name = (
        collection_qualified_name + "--" + get_qualified_name(topic)
    )

    return Dataset.from_dict(
        {
            "name": topic,
            "collection": collection_qualified_name,
            "qualifiedName": dataset_qualified_name,
        }
    )


def build_field(
    name: str,
    dataset_qualified_name: str,
    type_name: str,
    definition: Union[str, None] = None,
) -> DataField:
    return DataField.from_dict(
        {
            "name": name,
            "dataset": dataset_qualified_name,
            "definition": definition,
            "qualifiedName": f"{dataset_qualified_name}--{get_qualified_name(name)}",
            "fieldType": type_name,
        }
    )


def parse_avro_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse an Avro schema and yield DataField instances."""
    avro_schema = loads(schema)
    for field in avro_schema.fields:
        yield build_field(
            name=field.name,
            dataset_qualified_name=dataset_qualified_name,
            definition=field.doc,
            type_name=field.type.name,
        )


def parse_json_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse a JSON schema and yield DataField instances."""
    schema_dict = json.loads(schema)
    for field, metadata in schema_dict.get("properties", {}).items():
        yield build_field(
            name=field,
            dataset_qualified_name=dataset_qualified_name,
            definition=metadata.get("description"),
            type_name=metadata.get("type"),
        )


# Inverted index of data types to standardized names
DATA_TYPE_MAPPING = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "dict": "object",
    "list": "array",
    "bytes": "binary",
}


def parse_json_payload(
    payload: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse a JSON payload and yield DataField instances."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logging.error("Invalid JSON payload")
        return

    if not isinstance(data, dict):
        logging.error("JSON payload is not a dictionary")
        return

    for field, value in data.items():
        if isinstance(value, dict):
            type_name = value.get("type", "object")
        else:
            type_name = type(value).__name__

        yield build_field(
            name=field,
            dataset_qualified_name=dataset_qualified_name,
            type_name=DATA_TYPE_MAPPING.get(type_name, type_name),
        )


Parser = Callable[[str, str], Generator[DataField, None, None]]

SCHEMA_PARSERS: Dict[str, Parser] = {
    "avro": parse_avro_schema,
    "json": parse_json_schema,
}


def discover_cluster(
    admin_client: AdminClient,
    consumer: Union[Consumer, None],
    schema_registry_client: Union[SchemaRegistryClient, None],
) -> Generator[ToAtlasConvertible, None, None]:
    """Main function to execute the Kafka topic message consumption process."""
    system = build_system("kafka_system")

    yield system

    cluster_id = get_cluster_id(admin_client)

    collection = build_collection(
        cluster_id or "kafka_collection", system.qualified_name
    )

    yield collection

    datasets = [
        build_dataset(topic, collection.qualified_name)
        for topic in get_external_topic_names(admin_client)
    ]

    yield from datasets

    if not (consumer and schema_registry_client):
        logging.warning(
            "No consumer or schema registry client provided. Skipping schema parsing."
        )
        return

    for topic in datasets:
        if not (data := consume_message(topic.name, consumer)):
            logging.warning(f"No data found for topic: {topic.name}")
            continue

        if not (schema := get_message_schema(data, schema_registry_client)):
            logging.info(
                f"No schema found for topic: {topic.name}. Attempting to parse as JSON payload."
            )

            yield from parse_json_payload(
                payload=data.decode("utf-8"),
                dataset_qualified_name=topic.qualified_name,
            )

            continue

        if not (parser := SCHEMA_PARSERS.get(schema.schema_type.lower())):
            logging.warning(
                f"No parser found for schema type: {schema.schema_type} in topic: {topic.name}"
            )
            continue

        yield from parser(schema.schema_str, topic.qualified_name)


async def create_from_kafka(
    admin_client: AdminClient,
    consumer: Union[Consumer, None],
    schema_registry_client: Union[SchemaRegistryClient, None],
    access_token: str,
):
    """Scan a Kafka cluster and create Atlas entities from the discovered topics."""
    for entity in discover_cluster(
        admin_client=admin_client,
        consumer=consumer,
        schema_registry_client=schema_registry_client,
    ):
        atlas_compatible = entity.convert_to_atlas()
        await get_ref_and_push([atlas_compatible], False, access_token)
