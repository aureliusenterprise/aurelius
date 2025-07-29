import json
import logging
from typing import Callable, Dict, Generator, List, Union

from avro.schema import RecordSchema
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
    *,
    definition: Union[str, None] = None,
    parent_field: Union[str, None] = None,
) -> DataField:
    return DataField.from_dict(
        {
            "name": name,
            "dataset": dataset_qualified_name,
            "definition": definition,
            "qualifiedName": f"{dataset_qualified_name}--{get_qualified_name(name)}",
            "fieldType": type_name,
            "parentField": parent_field,
        }
    )


def _parse_avro_schema(
    schema: RecordSchema,
    dataset_qualified_name: str,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    for field in schema.fields:
        type_name = (
            " | ".join(schema.name for schema in field.type.schemas)
            if field.type.type == "union"
            else field.type.name
        )

        result = build_field(
            name=field.name,
            dataset_qualified_name=dataset_qualified_name,
            definition=field.doc,
            parent_field=parent_field,
            type_name=type_name,
        )

        yield result

        if field.type.type == "record":
            # Recursively parse nested records
            yield from _parse_avro_schema(
                schema=field.type,
                dataset_qualified_name=dataset_qualified_name,
                parent_field=result.qualified_name,
            )
        elif field.type.type == "array":
            # If the field is an array, parse its items
            items = field.type.items
            if items.type == "record":
                yield from _parse_avro_schema(
                    schema=items,
                    dataset_qualified_name=dataset_qualified_name,
                    parent_field=result.qualified_name,
                )
            else:
                # For non-record items, just yield the field
                yield build_field(
                    name=f"{field.name}_item",
                    dataset_qualified_name=dataset_qualified_name,
                    type_name=items.name,
                    parent_field=result.qualified_name,
                )


def parse_avro_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse an Avro schema and yield DataField instances."""
    yield from _parse_avro_schema(
        schema=loads(schema),
        dataset_qualified_name=dataset_qualified_name,
    )


def _get_json_schema_definition(ref: str, defs: dict) -> Union[dict, None]:
    return defs.get(ref.replace("#/$defs/", ""))


def _find_json_schema_references(
    schema: dict,
    defs: dict,
) -> Generator[dict, None, None]:
    dependencies = [
        *schema.get("anyOf", []),
        *schema.get("allOf", []),
        *schema.get("oneOf", []),
    ]

    if items := schema.get("items"):
        dependencies.append(items)

    for dep in dependencies:
        if ref := dep.get("$ref"):
            if definition := _get_json_schema_definition(ref, defs):
                yield definition

        yield from _find_json_schema_references(dep, defs)


def _parse_json_schema_type(schema: dict, defs: dict) -> str:
    """Parse the type from a JSON schema."""

    if ref := schema.get("$ref"):
        if definition := _get_json_schema_definition(ref, defs):
            return _parse_json_schema_type(definition, defs)

    type_name = schema.get("type", "object")

    if "anyOf" in schema:
        return " | ".join(
            _parse_json_schema_type(item, defs) for item in schema["anyOf"]
        )

    if "allOf" in schema:
        return " & ".join(
            _parse_json_schema_type(item, defs) for item in schema["allOf"]
        )

    if "oneOf" in schema:
        return " ^ ".join(
            _parse_json_schema_type(item, defs) for item in schema["oneOf"]
        )

    if type_name == "array":
        items = schema.get("items", {})
        if isinstance(items, dict):
            return f"array<{_parse_json_schema_type(items, defs)}>"
        return "array"
    
    if type_name == "object":
        return schema.get("title", "object")

    return type_name


def _parse_json_schema(
    schema: dict,
    dataset_qualified_name: str,
    defs: dict,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    for key, metadata in schema.get("properties", {}).items():
        type_name = _parse_json_schema_type(metadata, defs)

        field = build_field(
            name=key,
            dataset_qualified_name=dataset_qualified_name,
            definition=metadata.get("description"),
            parent_field=parent_field,
            type_name=type_name,
        )

        yield field

        for definition in _find_json_schema_references(metadata, defs):
            yield from _parse_json_schema(
                schema=definition,
                dataset_qualified_name=dataset_qualified_name,
                defs=defs,
                parent_field=field.qualified_name,
            )


def parse_json_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse a JSON schema and yield DataField instances."""
    schema_dict = json.loads(schema)

    yield from _parse_json_schema(
        schema=schema_dict,
        dataset_qualified_name=dataset_qualified_name,
        defs=schema_dict.get("$defs", {}),
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


def _parse_json_payload(
    payload: dict,
    dataset_qualified_name: str,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    """Parse a JSON payload and yield DataField instances."""
    for key, value in payload.items():
        type_name = (
            value.get("type", "object")
            if isinstance(value, dict)
            else type(value).__name__
        )

        field = build_field(
            name=key,
            dataset_qualified_name=dataset_qualified_name,
            type_name=DATA_TYPE_MAPPING.get(type_name, type_name),
            parent_field=parent_field,
        )

        yield field

        if isinstance(value, dict):
            # Recursively parse nested objects
            yield from _parse_json_payload(
                payload=value,
                dataset_qualified_name=dataset_qualified_name,
                parent_field=field.qualified_name,
            )


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

    yield from _parse_json_payload(
        payload=data,
        dataset_qualified_name=dataset_qualified_name,
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
