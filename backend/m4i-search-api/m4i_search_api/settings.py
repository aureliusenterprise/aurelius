from collections.abc import Hashable

from pydantic import Field, SecretStr, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings, Hashable):
    base_url: HttpUrl = Field(
        description="The base URL of the App Search instance, e.g., http://localhost:3002/",
    )

    password: SecretStr = Field(
        description="The password for authenticating with the App Search instance",
    )

    username: str = Field(
        description="The username for authenticating with the App Search instance",
    )

    timeout_seconds: int = Field(
        default=15,
        description="The timeout in seconds for requests to the App Search instance",
    )

    verify_ssl: bool = Field(
        default=True,
        description="Whether to verify SSL certificates when making requests",
    )

    model_config = {
        "env_prefix": "APP_SEARCH_",
        "frozen": True,
    }
