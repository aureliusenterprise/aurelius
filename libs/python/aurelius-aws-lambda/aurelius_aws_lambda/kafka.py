import base64
from datetime import datetime

from aws_lambda_powertools.shared.functions import decode_header_bytes
from pydantic import BaseModel, Field, field_validator


class AWSLambdaKafkaRecordBase(BaseModel):
    """Base model for Kafka records in AWS Lambda."""

    headers: list[dict[str, bytes]] = Field(
        default_factory=list,
        description="A list of headers for the record.",
    )

    offset: int = Field(
        description="The offset of the record in the partition.",
    )

    partition: int = Field(
        description="The partition from which the record was read.",
    )

    timestamp: datetime = Field(
        description="The timestamp of the record.",
    )

    timestamp_type: str = Field(
        alias="timestampType",
        description="The type of timestamp for the record.",
    )

    topic: str = Field(
        description="The topic from which the record was read.",
    )

    @field_validator("headers", mode="before")
    @classmethod
    def decode_headers(cls, headers: list[dict[str, str]]) -> list[dict[str, bytes]]:
        """Decode headers to bytes."""
        return [{key: decode_header_bytes(values) for key, values in header.items()} for header in headers]


class AWSLambdaKafkaRecord(AWSLambdaKafkaRecordBase):
    """Model representing a Kafka record."""

    key: bytes | None = Field(
        default=None,
        description="The key of the record.",
    )

    value: bytes | None = Field(
        default=None,
        description="The value of the record.",
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
