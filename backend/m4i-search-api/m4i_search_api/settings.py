from collections.abc import Hashable
from typing import Optional

from pydantic import Field, SecretStr, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings, Hashable):
    base_url: HttpUrl = Field(
        description="The base URL of the App Search instance, e.g., http://localhost:3002/",
    )

    ca_cert_path: Optional[str] = Field(
        default=None,
        description="Path to the CA certificate file for SSL verification. If not set, SSL verification is disabled.",
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

    model_config = {
        "env_prefix": "APP_SEARCH_",
        "frozen": True,
    }
