from collections.abc import Sequence
from uuid import UUID

from aurelius_sdk.postgresql import sanitize_tsquery
from pydantic import BaseModel, Field, HttpUrl, NonNegativeInt, PositiveInt, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

DEVELOPMENT = "development"


class Envelope[T: BaseModel | None](BaseModel):
    """A generic envelope model that wraps a value with a unique identifier."""

    guid: UUID = Field(
        description="The unique identifier for the value contained in the envelope.",
    )

    value: T = Field(
        description="The value contained in the envelope.",
    )


class PaginatedResponse[T: BaseModel](BaseModel):
    """A generic paginated response model that wraps paginated data with total count."""

    data: Sequence[T] = Field(
        description="The paginated results.",
    )

    total: int = Field(
        description="The total number of items matching the query filter, ignoring pagination.",
    )


class PaginationQueryParams(BaseModel):
    """Query parameters for pagination."""

    skip: NonNegativeInt = Field(
        default=0,
        description="Number of items to skip for pagination.",
    )

    limit: PositiveInt = Field(
        default=100,
        description="Maximum number of items to return per page.",
        le=1000,
    )


class FindAllQueryParams(PaginationQueryParams):
    """Query parameters for the find all endpoint."""

    search: str | None = Field(
        default=None,
        description="Optional search query to filter entities.",
    )

    @field_validator("search", mode="before")
    @classmethod
    def sanitize_search(cls, value: str | None) -> str | None:
        """
        Sanitize search query for PostgreSQL full-text search.

        Args:
            value: The raw search query string.

        Returns:
            Sanitized search query or None if input is empty/whitespace only.
        """
        return sanitize_tsquery(value)


class Settings(BaseSettings):
    """Application configuration settings."""

    environment: str = Field(
        default="production",
        description="The environment in which the application is running. Set to 'development' for local testing.",
    )

    auth_realm_name: str = Field(
        description="The name of the authentication realm.",
    )

    auth_server_url: HttpUrl = Field(
        description="The base URL of the authentication server.",
    )

    auto_create_schema: bool = Field(
        default_factory=lambda settings: settings.get("environment") == DEVELOPMENT,
        description="Automatically create the database schema. Enabled by default in development mode.",
    )

    cdc_epoll_timeout: float = Field(
        default=10.0,
        description="The timeout in seconds for epoll to wait for new events in the SSE endpoint.",
    )

    database_driver: str = Field(
        default="postgresql",
        description="The driver for the database.",
    )

    database_host: str = Field(
        default="localhost",
        description="The host for the database.",
    )

    database_name: str = Field(
        default="postgres",
        description="The name of the database.",
    )

    database_password: SecretStr = Field(
        description="The password for the database.",
    )

    database_port: int = Field(
        default=5432,
        description="The port for the database.",
    )

    database_username: str = Field(
        default="postgres",
        description="The username for the database.",
    )

    host: str = Field(
        default="127.0.0.1",
        description="The host to bind the server to.",
    )

    log_level: str = Field(
        default="INFO",
        description="The logging level for the application.",
    )

    port: int = Field(
        default=8000,
        description="The port to bind the server to.",
    )

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment == DEVELOPMENT

    @property
    def database_url(self) -> URL:
        """Construct the database URL."""
        return URL.create(
            drivername=self.database_driver,
            username=self.database_username,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )

    model_config = SettingsConfigDict(
        frozen=True,
    )
