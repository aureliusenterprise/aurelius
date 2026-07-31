"""Integration tests for the m4i-search-api health endpoint."""

import requests


def test__health_endpoint_returns_200(api_base_url: str) -> None:
    """The /health endpoint should return 200 OK."""
    response = requests.get(f"{api_base_url}/health", timeout=10)
    assert response.status_code == 200
