import base64

from pydantic import BaseModel, Field, field_validator


class AWSLambdaKafkaRecord(BaseModel):
    """Model representing a Kafka record."""

    key: bytes | None = Field(
        default=None,
        description="The key of the Kafka record.",
    )

    value: bytes | None = Field(
        default=None,
        description="The value of the Kafka record",
    )

    @field_validator("key", mode="before")
    @classmethod
    def deserialize_key(cls, key: str | None) -> bytes | None:
        """Deserialize the key from base64 to bytes."""
        return base64.b64decode(key) if key else None

    @field_validator("value", mode="before")
    @classmethod
    def deserialize_value(cls, value: str | None) -> bytes | None:
        """Deserialize the value from base64 to bytes."""
        return base64.b64decode(value) if value else None


class AWSLambdaKafkaEvent[T: BaseModel = AWSLambdaKafkaRecord](BaseModel):
    """Model for the Kafka events received by AWS Lambda."""

    records: dict[str, list[T]] = Field(
        default_factory=dict,
        description="A dictionary where the key is the partition name and the value is a list of records.",
    )
