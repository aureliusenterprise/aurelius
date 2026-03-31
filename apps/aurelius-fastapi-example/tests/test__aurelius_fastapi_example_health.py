from fastapi.testclient import TestClient


def test__ready_returns_200(authenticated_client: TestClient) -> None:
    """Healthcheck endpoint should return 200 OK."""
    response = authenticated_client.get("/health/ready")

    assert response.status_code == 200
    assert response.content == b"null"
