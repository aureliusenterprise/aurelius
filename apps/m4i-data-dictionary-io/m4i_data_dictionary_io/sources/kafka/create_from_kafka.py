import logging
from typing import Callable, Dict, Generator, Union

from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import (
    Schema,
    SchemaRegistryClient,
)

from m4i_data_dictionary_io.entities.json import (
    DataField,
    ToAtlasConvertible,
)
from m4i_data_dictionary_io.functions.create_from_excel import get_ref_and_push

from .admin import get_cluster_id, get_external_topic_names
from .atlas import build_collection, build_dataset, build_system
from .avro import parse_avro_schema
from .consumer import consume_message
from .json_schema import parse_json_schema
from .payload import parse_payload
from .schema_registry import get_message_schema, get_topic_schema

Parser = Callable[[str, str], Generator[DataField, None, None]]

SCHEMA_PARSERS: Dict[str, Parser] = {
    "avro": parse_avro_schema,
    "json": parse_json_schema,
}


def parse_schema(
    schema: Schema,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse a schema and yield DataField instances."""
    if schema.schema_type.lower() not in SCHEMA_PARSERS:
        logging.error(f"No parser found for schema type: {schema.schema_type}")
        return

    parser = SCHEMA_PARSERS[schema.schema_type.lower()]
    yield from parser(schema.schema_str, dataset_qualified_name)


def discover_cluster(
    admin_client: AdminClient,
    consumer: Union[Consumer, None],
    schema_registry_client: Union[SchemaRegistryClient, None],
    *,
    system_name: str = "kafka_system",
) -> Generator[ToAtlasConvertible, None, None]:
    """Main function to execute the Kafka topic message consumption process."""
    system = build_system(system_name)

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
        # Attempt to retrieve schema from Schema Registry
        if schema := get_topic_schema(topic.name, schema_registry_client):
            yield from parse_schema(schema, topic.qualified_name)

        # If no schema is found, consume a message to infer the schema from the payload
        elif data := consume_message(topic.name, consumer):
            # Attempt to retrieve schema from message header
            if schema := get_message_schema(data, schema_registry_client):
                yield from parse_schema(schema, topic.qualified_name)
            else:
                # If no schema is found, parse the raw payload
                yield from parse_payload(
                    payload=data.decode("utf-8"),
                    dataset_qualified_name=topic.qualified_name,
                )


async def create_from_kafka(
    admin_client: AdminClient,
    consumer: Union[Consumer, None],
    schema_registry_client: Union[SchemaRegistryClient, None],
    access_token: str,
    *,
    system_name: str = "kafka_system",
):
    """Scan a Kafka cluster and create Atlas entities from the discovered topics."""
    for entity in discover_cluster(
        admin_client=admin_client,
        consumer=consumer,
        schema_registry_client=schema_registry_client,
        system_name=system_name,
    ):
        atlas_compatible = entity.convert_to_atlas()
        await get_ref_and_push([atlas_compatible], False, access_token)
