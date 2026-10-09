from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from aurelius_atlas_server.app import create_app
from aurelius_atlas_server.settings import ServerSettings
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from fastapi.testclient import TestClient
from pydantic import SecretStr


@pytest.fixture
def settings() -> ServerSettings:
    """Return settings that never touch a real cluster."""
    return ServerSettings(
        elasticsearch=ElasticsearchSettings(password=SecretStr("x")),
        build_revision="abc123",
        _env_file=None,  # type: ignore[call-arg]
    )


@pytest.fixture
def store() -> MagicMock:
    """Return a stand-in Elasticsearch client whose cluster is green."""
    client = MagicMock()
    response = MagicMock()
    response.body = {"cluster_name": "c", "status": "green", "number_of_nodes": 1}
    client.cluster.health = AsyncMock(return_value=response)
    client.close = AsyncMock()
    return client


@pytest.fixture
def client(settings: ServerSettings, store: MagicMock) -> Iterator[TestClient]:
    """Return a test client for an app wired to the stand-in store."""
    with TestClient(create_app(settings, client_factory=lambda _: store)) as test_client:
        yield test_client
