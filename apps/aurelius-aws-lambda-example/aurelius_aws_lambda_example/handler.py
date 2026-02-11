import json
from functools import cache

from aurelius_aws_lambda import AWSLambdaKafkaEvent
from aurelius_example import Entity
from aurelius_kafka import KafkaProducer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient, record_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer

from aurelius_aws_lambda_example.globals import LOGGER, METADATA, SETTINGS
from aurelius_aws_lambda_example.processing import EntityProcessor


@cache
def initialize() -> tuple[EntityProcessor, KafkaProducer]:
    """Initialize the application."""
    schema_registry_client = SchemaRegistryClient(
        {"url": str(SETTINGS.schema_registry_url)},
    )

    value_schema = Entity.avro_schema(namespace="com.aureliusenterprise.example")

    deserializer = AvroDeserializer(
        conf={"subject.name.strategy": record_subject_name_strategy},  # type: ignore[arg-type]
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=json.dumps(value_schema),  # type: ignore[arg-type]
    )

    serializer = AvroSerializer(
        conf={"subject.name.strategy": record_subject_name_strategy},  # type: ignore[arg-type]
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=json.dumps(value_schema),  # type: ignore[arg-type]
    )

    processor = EntityProcessor(
        deserializer=deserializer,
        serializer=serializer,
    )

    kafka_producer = KafkaProducer(
        producer=Producer({"bootstrap.servers": SETTINGS.kafka_bootstrap_servers}),
    )

    name = METADATA["Name"]
    version = METADATA["Version"]

    LOGGER.info("Successfully initialized %s (%s)", name, version)
    LOGGER.debug("Settings: %s", SETTINGS)

    return processor, kafka_producer


@event_parser(model=AWSLambdaKafkaEvent)
def main(
    event: AWSLambdaKafkaEvent,
    context: LambdaContext,
) -> None:
    """Entry point for the Lambda function."""
    processor, producer = initialize()

    LOGGER.info("Start processing messages")
    LOGGER.debug("Received event: %s", event)
    LOGGER.debug("Context: %s", context)

    output = processor(event)

    producer.batch(
        topic=SETTINGS.kafka_topic_name,
        messages=output,
    )
