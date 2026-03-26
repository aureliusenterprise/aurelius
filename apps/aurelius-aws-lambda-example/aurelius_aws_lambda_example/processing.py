from collections.abc import Generator

from aurelius_aws_lambda.kafka import AWSLambdaKafkaEvent
from aurelius_example import Entity
from confluent_kafka.serialization import Deserializer, Serializer

from aurelius_aws_lambda_example.globals import LOGGER


class EntityProcessor:
    """A processor for handling entities in Kafka events."""

    def __init__(self, deserializer: Deserializer, serializer: Serializer) -> None:
        """Initialize the EntityProcessor with a deserializer and serializer."""
        self._deserializer = deserializer
        self._serializer = serializer

    def __call__(self, event: AWSLambdaKafkaEvent) -> Generator[tuple[bytes | None, bytes | None]]:
        """
        Process the Kafka event and yield serialized key-value pairs.

        Args:
            event (AWSLambdaKafkaEventModel): The Kafka event to process.

        Returns:
            Generator[tuple[bytes | None, bytes | None]]: A generator yielding key-value pairs.
        """
        deserialized_records = [
            (
                record.key,
                self.deserialize(record.value),
            )
            for records in event.records.values()
            for record in records
            if record.value is not None
        ]

        LOGGER.debug("Deserialized records: %s", deserialized_records)

        return (
            (
                key,
                self.serialize(entity),
            )
            for key, entity in deserialized_records
            if entity is not None
        )

    def deserialize(self, value: bytes | None) -> Entity | None:
        """
        Deserialize a value into an Entity.

        Args:
            value (bytes | None): The value to deserialize.

        Returns:
            Entity | None: The deserialized Entity or None if the value is None.
        """
        if value is None:
            return None

        entity_dict = self._deserializer(value)

        if entity_dict is None:
            return None

        return Entity.model_validate(entity_dict)

    def serialize(self, entity: Entity) -> bytes | None:
        """
        Serialize an Entity into bytes.

        Args:
            entity (Entity): The Entity to serialize.

        Returns:
            bytes: The serialized bytes of the Entity.
        """
        return self._serializer(entity.model_dump())
