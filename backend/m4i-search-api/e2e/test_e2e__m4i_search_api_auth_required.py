"""Integration tests for authentication enforcement on the search-api."""

import requests


def test__unauthenticated_request_returns_401(api_base_url: str) -> None:
    """Requests without an Authorization header should return 401."""
    response = requests.post(
        f"{api_base_url}/api/as/v1/engines/test-engine/search",
        json={"query": "test"},
        timeout=10,
    )
    assert response.status_code == 401


def test__invalid_token_returns_401(api_base_url: str) -> None:
    """Requests with an invalid Bearer token should return 401."""
    response = requests.post(
        f"{api_base_url}/api/as/v1/engines/test-engine/search",
        headers={"Authorization": "Bearer invalid-token"},
        json={"query": "test"},
        timeout=10,
    )
    assert response.status_code == 401
