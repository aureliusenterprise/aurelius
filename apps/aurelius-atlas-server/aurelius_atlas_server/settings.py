"""Server settings, read once at start-up from the environment (ADR 018)."""

from aurelius_atlas_store_es.settings import ElasticsearchSettings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PREFIX = "AURELIUS_ATLAS_SERVER_"


class ServerSettings(BaseSettings):
    """Everything the server needs to start.

    Environment variables use the prefix ``AURELIUS_ATLAS_SERVER_`` and ``__`` for nested
    values, for example ``AURELIUS_ATLAS_SERVER_ELASTICSEARCH__PASSWORD``. A ``.env`` file in the
    working directory is read too (development); real environment variables win.

    Attributes:
        host: Interface to listen on.
        port: Port to listen on (Atlas's own default is 21000).
        elasticsearch: How to reach the store; required (at least its password).
        build_revision: The commit this build was made from, reported as ``Revision``
            by the version endpoint (DV-03).
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX, env_nested_delimiter="__", env_file=".env", extra="ignore", frozen=True
    )

    host: str = "127.0.0.1"
    port: int = Field(default=21000, ge=1, le=65535)
    elasticsearch: ElasticsearchSettings
    build_revision: str = "unknown"


def load_settings() -> ServerSettings:
    """Read the settings from the environment.

    Returns:
        The settings.

    Raises:
        SystemExit: If a setting is invalid; the message lists every problem (fail loudly, ADR 018).
    """
    from pydantic import ValidationError  # noqa: PLC0415

    try:
        return ServerSettings()  # pyright: ignore[reportCallIssue] - fields come from the environment
    except ValidationError as error:
        raise SystemExit(str(error)) from error
