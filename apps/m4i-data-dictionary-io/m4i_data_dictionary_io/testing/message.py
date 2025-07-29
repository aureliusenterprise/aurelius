from pydantic import Field
from pydantic_avro.base import AvroBase


class Message(AvroBase):
    """A model representing a message with a topic and content."""

    content: str = Field(description="The content of the message")
    name: str = Field(description="The topic of the message")
    version: int = Field(default=1, description="The version of the message")
