"""Integration tests for authentication enforcement on the search-api."""

import requests


def test_unauthenticated_request_returns_401(api_base_url: str) -> None:
    """Requests without an Authorization header should return 401."""
    response = requests.get(f"{api_base_url}/api/as/v1/engines", timeout=10)
    assert response.status_code == 401


def test_invalid_token_returns_401(api_base_url: str) -> None:
    """Requests with an invalid Bearer token should return 401."""
    response = requests.get(
        f"{api_base_url}/api/as/v1/engines",
        headers={"Authorization": "Bearer invalid-token"},
        timeout=10,
    )
    assert response.status_code == 401
