from flask.testing import FlaskClient


def test__unauthorized_without_auth_header(client: FlaskClient) -> None:
    """Request without Authorization header returns 401."""
    response = client.post("/api/as/v1/engines/test-engine/search", json={"query": "test"})
    assert response.status_code == 401
