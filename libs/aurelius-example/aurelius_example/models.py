from uuid import UUID, uuid4

from pydantic_avro.to_avro.base import AvroBase
from sqlmodel import Field, SQLModel


class Entity(AvroBase, SQLModel, table=True):
    """A model that represents an simple entity that can be serialized to Avro and stored in a SQL database."""

    description: str | None = Field(
        default=None,
        description="A description of the entity",
        max_length=255,
    )

    guid: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the entity",
        primary_key=True,
    )

    name: str | None = Field(
        default=None,
        description="The name of the entity",
        max_length=100,
    )
