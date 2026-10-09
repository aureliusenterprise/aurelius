"""Connection settings for the Elasticsearch store.

The library never reads environment variables itself; the application builds an
:class:`ElasticsearchSettings` from its own configuration and passes it in.
"""

from typing import Self

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, SecretStr, model_validator

INDEX_PREFIX_PATTERN = r"^[a-z][a-z0-9_-]{0,31}$"


class ElasticsearchSettings(BaseModel):
    """How to reach the Elasticsearch cluster and how to name indices in it.

    Attributes:
        hosts: One or more node URLs.
        username: Basic-auth user; ``None`` disables authentication.
        password: Basic-auth password; required when ``username`` is set.
        index_prefix: Prefix of every index this system creates, so several
            installations can share one cluster (DD-004).
        request_timeout: Seconds before a single request times out.
        verify_certs: Whether TLS certificates are verified.
        ca_certs: Path to a CA bundle for TLS, if not the system default.
    """

    model_config = ConfigDict(frozen=True)

    hosts: tuple[AnyHttpUrl, ...] = Field(default=(AnyHttpUrl("http://localhost:9200"),), min_length=1)
    username: str | None = "elastic"
    password: SecretStr | None = None
    index_prefix: str = Field(default="atlas", pattern=INDEX_PREFIX_PATTERN)
    request_timeout: float = Field(default=10.0, gt=0)
    verify_certs: bool = True
    ca_certs: str | None = None

    @model_validator(mode="after")
    def _credentials_come_in_pairs(self) -> Self:
        """Reject a username without a password and vice versa."""
        if (self.username is None) != (self.password is None):
            msg = "username and password must be set together"
            raise ValueError(msg)
        return self

    @property
    def basic_auth(self) -> tuple[str, str] | None:
        """Return the ``(username, password)`` pair for the client, or ``None``."""
        if self.username is None or self.password is None:
            return None
        return (self.username, self.password.get_secret_value())

    @property
    def host_urls(self) -> list[str]:
        """Return the node URLs as plain strings, without a trailing slash."""
        return [str(host).rstrip("/") for host in self.hosts]
