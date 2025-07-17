from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, SecretStr
from pydantic_settings import BaseSettings

DEVELOPMENT = "development"


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


class Settings(BaseSettings):
    """Application configuration settings."""

    environment: str = Field(
        default="production",
        description="The environment in which the application is running. Set to 'development' for local testing.",
    )

    auto_create_schema: bool = Field(
        default_factory=lambda settings: settings.get("environment") == DEVELOPMENT,
        description="Automatically create the database schema. Enabled by default in development mode.",
    )

    host: str = Field(
        default="127.0.0.1",
        description="The host to bind the server to.",
    )

    port: int = Field(
        default=8000,
        description="The port to bind the server to.",
    )

    postgres_db: str = Field(
        default="postgres",
        description="The name of the Postgres database.",
    )

    postgres_host: str = Field(
        default="localhost",
        description="The host for the Postgres database.",
    )

    postgres_password: SecretStr = Field(
        description="The password for the Postgres database.",
    )

    postgres_port: int = Field(
        default=5432,
        description="The port for the Postgres database.",
    )

    postgres_user: str = Field(
        default="postgres",
        description="The username for the Postgres database.",
    )

    log_level: str = Field(
        default="INFO",
        description="The logging level for the application.",
    )

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment == DEVELOPMENT

    @property
    def database_connection_string(self) -> str:
        """Construct the database connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
