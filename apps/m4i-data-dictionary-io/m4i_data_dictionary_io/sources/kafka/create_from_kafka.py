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

    print(f"Discovering Kafka cluster: {system_name}")
    yield system

    cluster_id = get_cluster_id(admin_client)

    collection = build_collection(
        cluster_id or "kafka_collection", system.qualified_name
    )

    print(f"Discovered Kafka cluster with ID: {cluster_id}")
    yield collection

    topics = get_external_topic_names(admin_client)
    if not topics:
        print("No topics found in the Kafka cluster.")
        return

    for topic in topics:
        dataset = build_dataset(
            topic,
            collection.qualified_name,
        )
        print(f"Processing topic: {topic}")
        yield dataset

        # Attempt to retrieve a schema for the topic from the Schema Registry
        schema = (
            get_topic_schema(topic, schema_registry_client)
            if schema_registry_client
            else None
        )
        print(f"Schema for topic {topic}: {schema}")
        data = consume_message(topic, consumer) if consumer and not schema else None
        print(f"Data for topic {topic}: {data}")

        if data and schema_registry_client and not schema:
            print(f"Fetching schema for topic: {topic} from Schema Registry")
            schema = get_message_schema(data, schema_registry_client)

        # Parse the schema if available
        if schema:
            print(f"Parsing schema for topic: {topic}")
            yield from parse_schema(
                schema,
                dataset.qualified_name,
            )
        # If no schema is found, but data is available, parse the payload
        elif data:
            print(f"No schema found for topic: {topic}, parsing payload")
            yield from parse_payload(
                data.decode("utf-8"),
                dataset.qualified_name,
            )
        else:
            print(f"No data or schema available for topic: {topic}, skipping parsing")
            continue


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
