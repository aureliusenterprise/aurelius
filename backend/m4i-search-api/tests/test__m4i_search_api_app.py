import re
from unittest.mock import Mock

import responses
from flask.testing import FlaskClient
from m4i_search_api.app import build_target_url
from m4i_search_api.settings import Settings
from typing import cast


def test__health_endpoint_returns_200(client: FlaskClient) -> None:
    """GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200


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
def test__proxy_replaces_authorization_header(client: FlaskClient) -> None:
    """The incoming Bearer token is replaced with the App Search API key."""
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"results": []},
    )

    client.get(
        "/api/as/v1/search/test-engine",
        headers={"Authorization": "Bearer user-token"},
    )

    # Verify the outgoing request used the App Search key, not the user token
    assert len(responses.calls) == 1

    call = cast("responses.Call", responses.calls[0])
    outgoing_auth = call.request.headers.get("Authorization")

    assert outgoing_auth == "Bearer test-search-key"


@responses.activate
def test__proxy_preserves_other_headers(client: FlaskClient) -> None:
    """Non-auth headers pass through to the backend."""
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"results": []},
    )

    client.get(
        "/api/as/v1/search/test-engine",
        headers={
            "Authorization": "Bearer user-token",
            "Content-Type": "application/json",
            "X-Custom-Header": "custom-value",
        },
    )

    assert len(responses.calls) == 1

    call = cast("responses.Call", responses.calls[0])

    assert call.request.headers.get("X-Custom-Header") == "custom-value"


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


def test__build_target_url_with_path(settings: Settings) -> None:
    """URL is correctly constructed with a path."""
    url = build_target_url(settings, "api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"


def test__build_target_url_with_trailing_slash_in_base(settings: Settings) -> None:
    """Trailing slash in base URL is handled correctly."""
    settings_with_slash = Mock(
        spec=Settings,
        base_url="http://app-search.test/",
    )
    url = build_target_url(settings_with_slash, "api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"


def test__build_target_url_with_empty_path(settings: Settings) -> None:
    """Empty path returns just the base URL."""
    url = build_target_url(settings, "")
    assert url == "http://app-search.test"


def test__build_target_url_with_leading_slash_in_path(settings: Settings) -> None:
    """Leading slash in path is handled correctly."""
    url = build_target_url(settings, "/api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"


def test__unauthorized_without_auth_header(client: FlaskClient) -> None:
    """Request without Authorization header returns 401."""
    response = client.get("/api/as/v1/search/test-engine")
    assert response.status_code == 401


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
