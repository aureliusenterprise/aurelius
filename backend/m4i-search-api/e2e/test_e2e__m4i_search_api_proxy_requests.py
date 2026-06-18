"""Integration tests for proxy request forwarding through the search-api."""

import pytest
import requests


@pytest.mark.parametrize("endpoint", ["search", "search.json"])
def test__proxy_post_request(
    api_base_url: str, api_session: requests.Session, app_search_engine: str, endpoint: str
) -> None:
    """An authenticated POST search.json request should be proxied to App Search."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines/{app_search_engine}/{endpoint}", json={"query": "test"}, timeout=10
    )
    assert response.status_code == 200


def test__proxy_should_return_403_for_disallowed_endpoints(
    api_base_url: str, api_session: requests.Session, app_search_engine: str
) -> None:
    """Disallowed write endpoints should return 403."""
    response = api_session.post(
        f"{api_base_url}/api/as/v1/engines/{app_search_engine}/documents",
        json={"id": "1", "name": "forbidden"},
        timeout=10,
    )
    assert response.status_code == 403


def test__proxy_should_return_403_for_disallowed_methods(
    api_base_url: str, api_session: requests.Session, app_search_engine: str
) -> None:
    """GET requests on search endpoints should be denied."""
    response = api_session.get(
        f"{api_base_url}/api/as/v1/engines/{app_search_engine}/search.json", timeout=10
    )
    assert response.status_code == 403
