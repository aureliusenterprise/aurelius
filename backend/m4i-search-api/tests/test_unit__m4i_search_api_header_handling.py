from typing import cast

import pytest
import responses
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

from m4i_search_api.routes.proxy import FILTERED_HEADERS, _build_proxy_headers


def test__replaces_authorization_with_api_key() -> None:
    """Authorization header is set to Bearer <api_key>."""
    headers = Headers()
    headers.add("Authorization", "Bearer user-token")
    result = _build_proxy_headers(headers, "my-api-key")
    assert result["Authorization"] == "Bearer my-api-key"


@pytest.mark.parametrize("header", FILTERED_HEADERS)
def test__filters_hop_by_hop_headers(header: str) -> None:
    """Hop-by-hop headers are stripped from the outgoing request."""
    headers = Headers({header.capitalize(): "value"})

    result = _build_proxy_headers(headers, "key")

    assert header.capitalize() not in result, f"Header {header} should be filtered"


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
def test__integration_hop_by_hop_headers_not_forwarded(client: FlaskClient) -> None:
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
def test__integration_preserves_content_type(client: FlaskClient) -> None:
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
def test__integration_preserves_custom_headers(client: FlaskClient) -> None:
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
