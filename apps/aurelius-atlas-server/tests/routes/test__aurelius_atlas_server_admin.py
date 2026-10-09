from unittest.mock import AsyncMock, MagicMock

import pytest
from elasticsearch import ConnectionError as EsConnectionError
from fastapi.testclient import TestClient


@pytest.mark.covers("aurelius_atlas_server.routes.admin.version", rules=["ADM-01"])
@pytest.mark.covers("aurelius_atlas_server.routes.admin.get_settings")
def test__version_reports_atlas_release_and_build(client: TestClient) -> None:
    """The version answer names the implemented Atlas release and this build's revision."""
    response = client.get("/api/atlas/admin/version")

    assert response.status_code == 200
    assert response.json() == {
        "Version": "2.4.0",
        "Revision": "abc123",
        "Name": "apache-atlas",
        "Description": "Metadata Management and Data Governance Platform over Hadoop",
    }


@pytest.mark.covers("aurelius_atlas_server.routes.admin.status", rules=["ADM-03"])
def test__status_is_active(client: TestClient) -> None:
    """Without a passive mode the server is always ACTIVE."""
    assert client.get("/api/atlas/admin/status").json() == {"Status": "ACTIVE"}


@pytest.mark.covers("aurelius_atlas_server.routes.admin.liveness", rules=["ADM-04"])
def test__liveness_text(client: TestClient) -> None:
    """Liveness answers with Atlas's plain text."""
    response = client.get("/api/atlas/admin/liveness")

    assert (response.status_code, response.text) == (200, "Service is live")
    assert response.headers["content-type"].startswith("text/plain")


@pytest.mark.covers("aurelius_atlas_server.routes.admin.readiness", rules=["ADM-05"])
@pytest.mark.covers("aurelius_atlas_server.routes.admin.get_store")
def test__readiness_when_store_is_available(client: TestClient, store: MagicMock) -> None:
    """Ready while the store is green or yellow; the check does not wait long."""
    response = client.get("/api/atlas/admin/readiness")

    assert (response.status_code, response.text) == (200, "Service is ready to accept requests")
    store.cluster.health.assert_awaited_once_with(wait_for_status="yellow", timeout="1s")


@pytest.mark.covers("aurelius_atlas_server.routes.admin.readiness", rules=["ADM-05", "ERR-01"])
@pytest.mark.covers("aurelius_atlas_server.errors.atlas_error_handler", rules=["ERR-01"])
@pytest.mark.parametrize("failure", ["red", "unreachable"])
def test__readiness_fails_like_atlas(client: TestClient, store: MagicMock, failure: str) -> None:
    """A red or unreachable store answers 500 with Atlas's error body and no errorCause."""
    if failure == "red":
        store.cluster.health.return_value.body = {"cluster_name": "c", "status": "red", "number_of_nodes": 1}
    else:
        store.cluster.health = AsyncMock(side_effect=EsConnectionError("down"))

    response = client.get("/api/atlas/admin/readiness")

    assert response.status_code == 500
    assert response.json() == {
        "errorCode": "ATLAS-500-00-001",
        "errorMessage": "Internal server error Service not ready to accept client requests",
    }
