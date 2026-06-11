import responses
from flask.testing import FlaskClient


@responses.activate
def test__proxy_forwards_get_request(client: FlaskClient) -> None:
    """Proxy forwards an allowed POST search request and returns response."""
    responses.add(
        responses.POST,
        "http://app-search.test/api/as/v1/engines/test-engine/search",
        status=200,
        json={"results": [{"id": "1", "title": "Test Result"}]},
    )

    response = client.post(
        "/api/as/v1/engines/test-engine/search",
        headers={"Authorization": "Bearer user-token"},
        json={"query": "test"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"results": [{"id": "1", "title": "Test Result"}]}


@responses.activate
def test__proxy_forwards_post_request_with_body(client: FlaskClient) -> None:
    """Proxy forwards an allowed POST search.json request with JSON body."""
    responses.add(
        responses.POST,
        "http://app-search.test/api/as/v1/engines/test-engine/search.json",
        status=200,
        json={"results": []},
    )

    response = client.post(
        "/api/as/v1/engines/test-engine/search.json",
        headers={"Authorization": "Bearer user-token"},
        json={"query": "test"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"results": []}


@responses.activate
def test__proxy_returns_error_status_from_backend(client: FlaskClient) -> None:
    """If App Search returns an error, the proxy returns the same status."""
    responses.add(
        responses.POST,
        "http://app-search.test/api/as/v1/engines/test-engine/search",
        status=500,
        json={"error": "Internal Server Error"},
    )

    response = client.post(
        "/api/as/v1/engines/test-engine/search",
        headers={"Authorization": "Bearer user-token"},
        json={"query": "test"},
    )

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal Server Error"}


@responses.activate
def test__proxy_with_root_path(client: FlaskClient) -> None:
    """Request to a disallowed route returns 403 and is not proxied."""
    response = client.post(
        "/api/as/v1/engines/test-engine/documents",
        headers={"Authorization": "Bearer user-token"},
        json={"query": "test"},
    )

    assert response.status_code == 403
    assert response.get_json() == {"error": "Route not allowed"}
    assert len(responses.calls) == 0


def test__proxy_disallows_get_on_allowed_path(client: FlaskClient) -> None:
    """GET requests are rejected even on allowlisted paths."""
    response = client.get(
        "/api/as/v1/engines/test-engine/search", headers={"Authorization": "Bearer user-token"}
    )

    assert response.status_code == 403
    assert response.get_json() == {"error": "Route not allowed"}
