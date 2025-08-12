import logging
from typing import Union

from confluent_kafka.schema_registry import (
    Schema,
    SchemaRegistryClient,
    SchemaRegistryError,
)

SCHEMA_REGISTRY_MAGIC_BYTE = b"\x00"


def get_topic_schema(
    topic: str,
    schema_registry_client: SchemaRegistryClient,
) -> Union[Schema, None]:
    """Retrieve the schema for a Kafka topic using topic name strategy."""
    try:
        return schema_registry_client.get_latest_version(f"{topic}-value").schema
    except SchemaRegistryError:
        print(f"Failed to retrieve schema for topic {topic}")
        logging.error(f"Failed to retrieve schema for topic {topic}")
        return None


def get_message_schema(
    message: bytes,
    schema_registry_client: SchemaRegistryClient,
) -> Union[Schema, None]:
    """Retrieve the schema for a Kafka message based on the schema registry header."""
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
