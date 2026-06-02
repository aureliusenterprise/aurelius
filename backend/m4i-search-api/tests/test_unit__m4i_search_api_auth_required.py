from flask.testing import FlaskClient


def test__unauthorized_without_auth_header(client: FlaskClient) -> None:
    """Request without Authorization header returns 401."""
    response = client.get("/api/as/v1/search/test-engine")
    assert response.status_code == 401
