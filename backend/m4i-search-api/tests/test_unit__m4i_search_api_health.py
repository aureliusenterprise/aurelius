from flask.testing import FlaskClient


def test__health_endpoint_returns_200(client: FlaskClient) -> None:
    """GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
