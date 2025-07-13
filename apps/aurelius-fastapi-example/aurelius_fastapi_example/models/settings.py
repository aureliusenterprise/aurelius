from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    environment: str = Field(
        default="production",
        description="The environment in which the application is running. Set to 'development' for local testing.",
    )

    host: str = Field(
        default="127.0.0.1",
        description="The host to bind the server to.",
    )

    port: int = Field(
        default=8000,
        description="The port to bind the server to.",
    )

    log_level: str = Field(
        default="INFO",
        description="The logging level for the application.",
    )

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment == "development"
