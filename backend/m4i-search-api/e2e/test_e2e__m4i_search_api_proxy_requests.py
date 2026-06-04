"""Integration tests for proxy request forwarding through the search-api."""

import requests


def test__proxy_get_request(api_base_url: str, api_session: requests.Session) -> None:
    """An authenticated POST search request should be proxied to App Search."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines/test-engine/search",
        json={"query": "test"},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")


def test__proxy_post_request(api_base_url: str, api_session: requests.Session) -> None:
    """An authenticated POST search.json request should be proxied to App Search."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines/test-engine/search.json",
        json={"query": "test"},
        timeout=10,
    )
    assert response.status_code == 200


def test__proxy_preserves_path(
    api_base_url: str, api_session: requests.Session
) -> None:
    """Disallowed write endpoints should return 403."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines/test-engine/documents",
        json={"id": "1", "name": "forbidden"},
        timeout=10,
    )
    assert response.status_code == 403


def test__proxy_disallows_get_method(
    api_base_url: str, api_session: requests.Session
) -> None:
    """GET requests on search endpoints should be denied."""
    response = api_session.get(
        f"{api_base_url}/api/as/v1/engines/test-engine/search",
        timeout=10,
    )
    assert response.status_code == 403
