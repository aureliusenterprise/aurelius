import json
from base64 import b64decode
from functools import cache

from aurelius_example import Entity
from aws_lambda_powertools.utilities.kafka import ConsumerRecords, kafka_consumer
from aws_lambda_powertools.utilities.kafka.consumer_records import ConsumerRecordRecords
from aws_lambda_powertools.utilities.typing import LambdaContext
from confluent_kafka import Producer
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    header_schema_id_serializer,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext

from aurelius_aws_lambda_example.globals import LOGGER, METADATA, SETTINGS


@cache
def initialize() -> tuple[AvroDeserializer, AvroSerializer, Producer]:
    """Initialize the application."""
    schema_registry_client = SchemaRegistryClient(
        {"url": str(SETTINGS.schema_registry_url)},
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

    kafka_producer = Producer({"bootstrap.servers": SETTINGS.kafka_bootstrap_servers})

    name = METADATA["Name"]
    version = METADATA["Version"]

    LOGGER.info("Successfully initialized %s (%s)", name, version)
    LOGGER.debug("Settings: %s", SETTINGS)

    return value_deserializer, value_serializer, kafka_producer


@kafka_consumer
def main(event: ConsumerRecords, context: LambdaContext) -> None:
    """Entry point for the Lambda function."""
    value_deserializer, value_serializer, producer = initialize()

    LOGGER.info("Start processing messages")
    LOGGER.debug("Received event: %s", event)
    LOGGER.debug("Context: %s", context)

    def deserialize_record(record: ConsumerRecordRecords) -> tuple[bytes | None, Entity | None]:
        LOGGER.debug("Deserializing value for record: %s", record)

        key = b64decode(record.original_key) if record.original_key is not None else None

        entity_dict = value_deserializer(
            b64decode(record.original_value) if record.original_value is not None else None,
            SerializationContext(
                field=MessageField.VALUE,
                headers=record.headers,  # type: ignore[headers format is valid]
                topic=record.topic,
            ),
        )

        if entity_dict is None:
            LOGGER.info("Received empty value for key: %s", key)
            return key, None

        entity = Entity.model_validate(entity_dict)

        LOGGER.info("Received entity for key %s: %s", key, entity)

        return key, entity

    deserialized_records = [deserialize_record(record) for record in event.records]

    LOGGER.debug("Deserialized records: %s", deserialized_records)

    def produce(key: bytes | None, value: Entity | None) -> None:
        headers = {}

        serialized_value = value_serializer(
            value.model_dump(mode="json") if value is not None else None,
            SerializationContext(
                field=MessageField.VALUE,
                headers=headers,
                topic=SETTINGS.kafka_topic_name,
            ),
        )

        producer.produce(
            topic=SETTINGS.kafka_topic_name,
            key=key,
            value=serialized_value,
            headers=headers,
        )

    for key, value in deserialized_records:
        LOGGER.info("Processing record with key: %s", key)
        LOGGER.debug("Record value: %s", value)

        produce(key, value)

    producer.flush()

    LOGGER.info("Finished processing messages")
