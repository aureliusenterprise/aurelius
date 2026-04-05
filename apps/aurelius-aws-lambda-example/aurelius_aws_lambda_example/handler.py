import json
from functools import cache

from aurelius_example import Entity
from aws_lambda_powertools.utilities.kafka import ConsumerRecords, kafka_consumer
from aws_lambda_powertools.utilities.typing import LambdaContext
from confluent_kafka import Producer
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    header_schema_id_serializer,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer

from aurelius_aws_lambda_example.globals import LOGGER, METADATA
from aurelius_aws_lambda_example.models import Settings
from aurelius_aws_lambda_example.processor import process


@cache
def initialize() -> tuple[Settings, AvroDeserializer, AvroSerializer, Producer]:
    """Initialize the application."""
    settings = Settings()  # type: ignore[load settings from environment variables]

    LOGGER.setLevel(settings.log_level)
    LOGGER.log_uncaught_exceptions = settings.is_development

    schema_registry_client = SchemaRegistryClient(
        {"url": str(settings.schema_registry_url)},
    )

    value_schema = Entity.avro_schema(namespace="com.aureliusenterprise.example")

    value_deserializer = AvroDeserializer(
        conf={"subject.name.strategy": record_subject_name_strategy},  # type: ignore[arg-type]
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=json.dumps(value_schema),  # type: ignore[arg-type]
    )

    value_serializer = AvroSerializer(
        conf={  # type: ignore[arg-type]
            "schema.id.serializer": header_schema_id_serializer,
            "subject.name.strategy": record_subject_name_strategy,
        },
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=json.dumps(value_schema),  # type: ignore[arg-type]
    )

    kafka_producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})

    name = METADATA["Name"]
    version = METADATA["Version"]

    LOGGER.info("Successfully initialized %s (%s)", name, version)
    LOGGER.debug("Settings: %s", settings)

    if settings.is_development:
        LOGGER.warning("🚨 Running in development mode. Not for production use! 🚨")

    return settings, value_deserializer, value_serializer, kafka_producer


@kafka_consumer
def main(event: ConsumerRecords, context: LambdaContext) -> None:
    """Entry point for the Lambda function."""
    settings, value_deserializer, value_serializer, producer = initialize()

    LOGGER.debug("Received event: %s", event)
    LOGGER.debug("Context: %s", context)

    process(
        event,
        topic_name=settings.kafka_topic_name,
        value_deserializer=value_deserializer,
        value_serializer=value_serializer,
        producer=producer,
    )
