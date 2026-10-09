from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from aurelius_atlas_store_es.client import (
    ClusterHealth,
    StoreUnavailableError,
    check_health,
    create_client,
)
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from elastic_transport import ApiResponseMeta, HttpHeaders, NodeConfig
from elasticsearch import ApiError, AsyncElasticsearch
from elasticsearch import ConnectionError as EsConnectionError
from pydantic import AnyHttpUrl

HEALTH = {"cluster_name": "c", "status": "green", "number_of_nodes": 1, "timed_out": False, "active_shards": 3}


def _client_returning(body: dict[str, object] | None = None, error: Exception | None = None) -> MagicMock:
    """Return a stand-in client whose cluster.health answers with ``body`` or raises ``error``."""
    client = MagicMock()
    response = MagicMock()
    response.body = body
    client.cluster.health = AsyncMock(return_value=response, side_effect=error)
    return client


def _as_client(mock: MagicMock) -> AsyncElasticsearch:
    """Present the stand-in where the code expects a real client."""
    return cast("AsyncElasticsearch", mock)


def _api_error(status: int, message: str) -> ApiError:
    """Build an ApiError as the client raises it for an HTTP error answer."""
    meta = ApiResponseMeta(
        status=status,
        http_version="1.1",
        headers=HttpHeaders(),
        duration=0.0,
        node=NodeConfig("http", "localhost", 9200),
    )
    return ApiError(message, meta=meta, body={})


@pytest.mark.covers("aurelius_atlas_store_es.client.create_client", rules=["ESI-05"])
async def test__create_client_uses_settings(settings: ElasticsearchSettings) -> None:
    """The client targets the configured hosts with basic auth and the configured timeout."""
    client = create_client(settings)
    try:
        node = next(iter(client.transport.node_pool.all()))
        assert node.config.host == "localhost"
        assert node.config.port == 9200
        assert client._headers["authorization"].startswith("Basic ")  # noqa: SLF001
        assert client._request_timeout == 10.0  # noqa: SLF001
    finally:
        await client.close()


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-06"])
async def test__check_health_parses_answer() -> None:
    """The health answer becomes a ClusterHealth; unknown fields are ignored."""
    client = _client_returning(HEALTH)

    health = await check_health(_as_client(client), wait_for_status="green", wait_timeout="3s")

    assert health == ClusterHealth(cluster_name="c", status="green", number_of_nodes=1)
    client.cluster.health.assert_awaited_once_with(wait_for_status="green", timeout="3s")


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-07"])
async def test__check_health_returns_red_without_raising() -> None:
    """A red cluster is reported, not raised, and is not available."""
    health = await check_health(_as_client(_client_returning({**HEALTH, "status": "red"})))

    assert health.status == "red"
    assert not health.is_available


@pytest.mark.covers("aurelius_atlas_store_es.client.ClusterHealth.is_available", rules=["ESI-07"])
@pytest.mark.parametrize(("status", "available"), [("green", True), ("yellow", True), ("red", False)])
def test__cluster_health_availability(status: str, available: bool) -> None:  # noqa: FBT001
    """Green and yellow clusters serve requests; red ones do not."""
    assert ClusterHealth.model_validate({**HEALTH, "status": status}).is_available is available


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-08"])
async def test__check_health_wraps_authentication_error() -> None:
    """Rejected credentials surface as StoreUnavailableError with the HTTP status."""
    client = _client_returning(error=_api_error(401, "security_exception"))

    with pytest.raises(StoreUnavailableError, match=r"HTTP 401"):
        await check_health(_as_client(client))


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-08"])
async def test__check_health_wraps_connection_error() -> None:
    """An unreachable cluster surfaces as StoreUnavailableError."""
    client = _client_returning(error=EsConnectionError("connection refused"))

    with pytest.raises(StoreUnavailableError, match="unreachable"):
        await check_health(_as_client(client))


@pytest.mark.covers("aurelius_atlas_store_es.client.create_client", rules=["ESI-05"])
async def test__create_client_with_custom_ca_bundle(settings: ElasticsearchSettings, tmp_path: Path) -> None:
    """A configured CA bundle is handed to the TLS layer."""
    bundle = tmp_path / "ca.pem"
    bundle.write_text("not a real certificate")
    with_ca = settings.model_copy(update={"ca_certs": str(bundle)})

    with pytest.raises(Exception, match=r"(?i)pem|certificate|ssl"):
        create_client(with_ca.model_copy(update={"hosts": (AnyHttpUrl("https://localhost:9200"),)}))
