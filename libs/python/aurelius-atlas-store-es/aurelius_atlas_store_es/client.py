"""Creating the Elasticsearch client and checking that the cluster is usable."""

from typing import Literal

from elasticsearch import ApiError, AsyncElasticsearch, TransportError
from pydantic import BaseModel, ConfigDict

from aurelius_atlas_store_es.settings import ElasticsearchSettings

HealthStatus = Literal["green", "yellow", "red"]


class StoreUnavailableError(RuntimeError):
    """The Elasticsearch cluster cannot be reached or refuses to serve requests."""


class ClusterHealth(BaseModel):
    """The part of the cluster health answer this system relies on.

    Attributes:
        cluster_name: Name of the cluster.
        status: ``green``, ``yellow`` or ``red``.
        number_of_nodes: Nodes currently in the cluster.
        timed_out: Whether the wait for the requested status timed out.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    cluster_name: str
    status: HealthStatus
    number_of_nodes: int
    timed_out: bool = False

    @property
    def is_available(self) -> bool:
        """Return whether the cluster can serve reads and writes (``green`` or ``yellow``)."""
        return self.status != "red"


def create_client(settings: ElasticsearchSettings) -> AsyncElasticsearch:
    """Create an asynchronous client for the configured cluster (DD-005).

    The client is not connected until its first request; call
    :func:`check_health` to verify the cluster is reachable.

    Args:
        settings: Connection settings.

    Returns:
        A new client. The caller owns it and must ``await client.close()``.
    """
    if settings.ca_certs is not None:
        return AsyncElasticsearch(
            hosts=settings.host_urls,
            basic_auth=settings.basic_auth,
            request_timeout=settings.request_timeout,
            verify_certs=settings.verify_certs,
            ca_certs=settings.ca_certs,
        )
    return AsyncElasticsearch(
        hosts=settings.host_urls,
        basic_auth=settings.basic_auth,
        request_timeout=settings.request_timeout,
        verify_certs=settings.verify_certs,
    )


async def check_health(
    client: AsyncElasticsearch,
    *,
    wait_for_status: HealthStatus = "yellow",
    wait_timeout: str = "10s",
) -> ClusterHealth:
    """Return the cluster health, waiting up to ``wait_timeout`` for ``wait_for_status``.

    Args:
        client: The client to use.
        wait_for_status: The status to wait for before answering.
        wait_timeout: How long Elasticsearch waits for that status, as an Elasticsearch
            time value such as ``"10s"``.

    Returns:
        The cluster health. A ``red`` status is returned, not raised; use
        :attr:`ClusterHealth.is_available` to decide.

    Raises:
        StoreUnavailableError: If the cluster cannot be reached, rejects the
            credentials, or answers with an error.
    """
    try:
        response = await client.cluster.health(wait_for_status=wait_for_status, timeout=wait_timeout)
    except ApiError as error:
        msg = f"Elasticsearch refused the health request (HTTP {error.meta.status}): {error.message}"
        raise StoreUnavailableError(msg) from error
    except TransportError as error:
        msg = f"Elasticsearch is unreachable: {error.message}"
        raise StoreUnavailableError(msg) from error
    return ClusterHealth.model_validate(dict(response.body))
