from unittest.mock import MagicMock

import pytest
from aurelius_atlas_server.app import create_app
from aurelius_atlas_server.settings import ServerSettings
from fastapi.testclient import TestClient


@pytest.mark.covers("aurelius_atlas_server.app.create_app", rules=["ADM-07"])
def test__create_app_opens_and_closes_store(settings: ServerSettings, store: MagicMock) -> None:
    """The store client is created from the settings at start-up and closed at shutdown."""
    seen = []

    def factory(es_settings: object) -> MagicMock:
        seen.append(es_settings)
        return store

    with TestClient(create_app(settings, client_factory=factory)) as client:
        assert client.get("/api/atlas/admin/status").status_code == 200
        store.close.assert_not_awaited()

    assert seen == [settings.elasticsearch]
    store.close.assert_awaited_once()


@pytest.mark.covers("aurelius_atlas_server.app.create_app", rules=["ADM-07"])
def test__create_app_serves_only_the_atlas_api(client: TestClient) -> None:
    """No interactive docs pages; the OpenAPI document lives under /api/atlas."""
    assert client.get("/docs").status_code == 404
    assert client.get("/api/atlas/openapi.json").json()["info"]["title"] == "Aurelius Atlas"
