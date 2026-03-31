from base64 import b64decode

from aurelius_example import Entity
from aws_lambda_powertools.utilities.kafka import ConsumerRecords
from aws_lambda_powertools.utilities.kafka.consumer_records import ConsumerRecordRecords
from confluent_kafka import Producer
from confluent_kafka._types import HeadersType
from confluent_kafka.serialization import Deserializer, MessageField, SerializationContext, Serializer

from aurelius_aws_lambda_example.globals import LOGGER


def deserialize(
    record: ConsumerRecordRecords,
    *,
    value_deserializer: Deserializer,
) -> tuple[bytes | None, Entity | None]:
    """
    Deserialize a Kafka record into an Entity instance.

    In addition to deserialing the value, this function also decodes the key and value from base64, as the Kafka event
    sent to Lambda by MSK is base64-encoded.

    Args:
        record (ConsumerRecordRecords): The Kafka record to deserialize.
        value_deserializer (Deserializer): The deserializer to use for deserializing the record value.
    """
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


def serialize(
    value: Entity | None,
    topic_name: str,
    headers: HeadersType | None = None,
    *,
    value_serializer: Serializer,
) -> tuple[HeadersType, bytes | None]:
    """
    Serialize a value for producing to Kafka.

    The value is serialized using the provided value_serializer. If no headers are provided,
    an empty list is used.

    Args:
        value (Entity | None): The value to serialize, which will be sent to Kafka.
        topic_name (str): The name of the Kafka topic to produce the record to.
        headers (HeadersType | None): Optional headers to include with the Kafka record.
        value_serializer (Serializer): The serializer to use for serializing the record value.

    Returns:
        tuple[HeadersType, bytes | None]: A tuple containing the headers and serialized value.
    """
    headers = headers if headers is not None else []

    serialized_value = value_serializer(
        value.model_dump(mode="json") if value is not None else None,
        SerializationContext(
            field=MessageField.VALUE,
            headers=headers,
            topic=topic_name,
        ),
    )

    return headers, serialized_value


def process(
    event: ConsumerRecords,
    topic_name: str,
    *,
    value_deserializer: Deserializer,
    value_serializer: Serializer,
    producer: Producer,
) -> None:
    """
    Process the incoming Kafka event by deserializing each record and producing the result to another Kafka topic.

    Args:
        event (ConsumerRecords): The incoming Kafka event containing the records to process.
        topic_name (str): The name of the Kafka topic to produce the processed records to.
        value_deserializer (Deserializer): The deserializer to use for deserializing the record values.
        value_serializer (Serializer): The serializer to use for serializing the record values before producing.
        producer (Producer): The Kafka producer to use for producing the processed records.
    """
    LOGGER.info("Start processing messages")

    deserialized_records = (
        deserialize(
            record,
            value_deserializer=value_deserializer,
        )
        for record in event.records
    )

    for key, value in deserialized_records:
        LOGGER.info("Processing record with key: %s", key)
        LOGGER.debug("Record value: %s", value)

        headers, serialized_value = serialize(
            value,
            topic_name=topic_name,
            value_serializer=value_serializer,
        )

        producer.produce(
            topic=topic_name,
            key=key,
            value=serialized_value,
            headers=headers,
        )

    producer.flush()

    LOGGER.info("Finished processing messages")
