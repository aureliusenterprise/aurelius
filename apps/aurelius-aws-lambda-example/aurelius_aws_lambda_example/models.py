from typing import Literal

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings

type Environment = Literal["development", "production"]


class Settings(BaseSettings):
    """Settings for the application."""

    aws_region: str = Field(
        description="AWS region for the application.",
    )

    environment: Environment = Field(
        default="production",
        description="The environment the application is running in.",
    )

    kafka_bootstrap_servers: str = Field(
        description="Comma-separated list of Kafka brokers to connect to.",
    )

    kafka_topic_name: str = Field(
        description="Name of the Kafka topic to produce messages to.",
    )

    log_level: str = Field(
        default="INFO",
        description="Minimum log level to display at runtime.",
    )

    schema_registry_url: HttpUrl = Field(
        description="URL of the schema registry.",
    )

    @property
    def is_development(self) -> bool:
        """Check if the application is running in a development environment."""
        return self.environment == "development"
