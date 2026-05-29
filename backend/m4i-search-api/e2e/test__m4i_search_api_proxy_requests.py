"""Integration tests for proxy request forwarding through the search-api."""

import requests


def test_proxy_get_request(api_base_url: str, api_session: requests.Session) -> None:
    """An authenticated GET request should be proxied to App Search."""
    response = api_session.get(f"{api_base_url}/api/as/v1/engines", timeout=10)
    # The proxy should forward the request and return a valid response
    # (200 OK with a JSON array of engines, or at least not an auth error)
    assert response.status_code in (200, 404)
    assert response.headers.get("Content-Type", "").startswith("application/json")


def test_proxy_post_request(api_base_url: str, api_session: requests.Session) -> None:
    """An authenticated POST request with a body should be proxied to App Search."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines",
        json={"name": "test-engine-proxy", "type": "default"},
        timeout=10,
    )
    # Either 200 (created) or 409 (already exists) — both indicate the request
    # was successfully proxied to App Search
    assert response.status_code in (200, 409)


def test_proxy_preserves_path(api_base_url: str, api_session: requests.Session) -> None:
    """The proxy should correctly forward the request path."""
    response = api_session.get(
        f"{api_base_url}/api/as/v1/engines/test-engine",
        timeout=10,
    )
    # Should return 200 (engine exists) or 404 (not found) — not an auth error
    assert response.status_code in (200, 404)
