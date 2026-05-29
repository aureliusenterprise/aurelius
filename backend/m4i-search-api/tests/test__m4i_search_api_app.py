import re
from unittest.mock import Mock

import responses
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from m4i_search_api.app import build_target_url, _build_proxy_headers
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


def test_replaces_authorization_with_api_key() -> None:
    """Authorization header is set to Bearer <api_key>."""
    headers = Headers()
    headers.add("Authorization", "Bearer user-token")
    result = _build_proxy_headers(headers, "my-api-key")
    assert result["Authorization"] == "Bearer my-api-key"


def test_filters_host_header() -> None:
    """Host header is never forwarded (it's hop-by-hop)."""
    headers = Headers()
    headers.add("Host", "original-host.com")
    result = _build_proxy_headers(headers, "key")
    assert "Host" not in result


def test_filters_hop_by_hop_headers() -> None:
    """Hop-by-hop headers are stripped from the outgoing request."""
    hop_by_hop = (
        "Connection",
        "Keep-Alive",
        "Proxy-Authenticate",
        "Proxy-Authorization",
        "TE",
        "Trailer",
        "Transfer-Encoding",
        "Upgrade",
    )
    headers = Headers()
    for h in hop_by_hop:
        headers.add(h, "value")
    result = _build_proxy_headers(headers, "key")
    for h in hop_by_hop:
        assert h not in result, f"Hop-by-hop header {h} should be filtered"


@responses.activate
def test_integration_hop_by_hop_headers_not_forwarded(client: FlaskClient) -> None:
    """
    Incoming hop-by-hop headers are not forwarded to the backend.

    Note: The `requests` library may add its own Connection header for keep-alive,
    so we verify that our custom hop-by-hop headers are filtered, not that the
    header is completely absent.
    """
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"ok": True},
    )

    client.get(
        "/api/as/v1/search/test-engine",
        headers={
            "Authorization": "Bearer user-token",
            "Keep-Alive": "timeout=5",
            "TE": "trailers",
            "Proxy-Authorization": "Basic proxy-creds",
        },
    )

    call = cast("responses.Call", responses.calls[0])
    # These headers should not be forwarded (requests won't add them itself)
    assert call.request.headers.get("Keep-Alive") is None
    assert call.request.headers.get("TE") is None
    assert call.request.headers.get("Proxy-Authorization") is None


@responses.activate
def test_integration_preserves_content_type(client: FlaskClient) -> None:
    """Content-Type header is preserved on the outgoing request."""
    responses.add(
        responses.POST,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"ok": True},
    )

    client.post(
        "/api/as/v1/search/test-engine",
        headers={
            "Authorization": "Bearer user-token",
            "Content-Type": "application/json",
        },
        json={"query": "test"},
    )

    call = cast("responses.Call", responses.calls[0])
    assert "application/json" in (call.request.headers.get("Content-Type") or "")


@responses.activate
def test_integration_preserves_custom_headers(client: FlaskClient) -> None:
    """Custom headers are forwarded to the backend."""
    responses.add(
        responses.GET,
        "http://app-search.test/api/as/v1/search/test-engine",
        status=200,
        json={"ok": True},
    )

    client.get(
        "/api/as/v1/search/test-engine",
        headers={
            "Authorization": "Bearer user-token",
            "X-Custom-Header": "custom-value",
            "X-Another-Header": "another-value",
        },
    )

    call = cast("responses.Call", responses.calls[0])
    assert call.request.headers.get("X-Custom-Header") == "custom-value"
    assert call.request.headers.get("X-Another-Header") == "another-value"
