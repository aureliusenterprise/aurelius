import re

import responses
from flask.testing import FlaskClient


@responses.activate
def test__proxy_forwards_get_request(client: FlaskClient) -> None:
    """Proxy forwards GET request to App Search and returns response."""
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"results": [{"id": "1", "title": "Test Result"}]},
    )

    response = client.get(
        "/api/as/v1/search/test-engine",
        headers={"Authorization": "Bearer user-token"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"results": [{"id": "1", "title": "Test Result"}]}


@responses.activate
def test__proxy_forwards_post_request_with_body(client: FlaskClient) -> None:
    """Proxy forwards POST request with JSON body to App Search."""
    responses.add(
        responses.POST,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"results": []},
    )

    response = client.post(
        "/api/as/v1/search/test-engine",
        headers={"Authorization": "Bearer user-token"},
        json={"query": "test"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"results": []}


@responses.activate
def test__proxy_returns_error_status_from_backend(client: FlaskClient) -> None:
    """If App Search returns an error, the proxy returns the same status."""
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=500,
        json={"error": "Internal Server Error"},
    )

    response = client.get(
        "/api/as/v1/search/test-engine",
        headers={"Authorization": "Bearer user-token"},
    )

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal Server Error"}


@responses.activate
def test__proxy_with_root_path(client: FlaskClient) -> None:
    """Request to / is proxied correctly."""
    responses.add(
        responses.GET,
        re.compile(r"http://app-search.test/?$"),
        status=200,
        json={"root": True},
    )

    response = client.get(
        "/",
        headers={"Authorization": "Bearer user-token"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"root": True}
