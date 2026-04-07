from typing import Any, Dict, List

import pytest

import m4i_search_api.app as app_module
from m4i_search_api.settings import AppSearchSettings


class DummyResponse:
    def __init__(self, content: bytes = b"{}", status_code: int = 200, content_type: str = "application/json"):
        self.content = content
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}


@pytest.fixture
def proxy_client(monkeypatch):
    captured_calls: List[Dict[str, Any]] = []

    def fake_request(**kwargs):
        captured_calls.append(kwargs)
        return DummyResponse(content=b'{"ok": true}', status_code=200)

    # Keep app creation focused on proxy behavior.
    monkeypatch.setattr(app_module, "register_shared", lambda app: None)
    monkeypatch.setattr(app_module, "requires_auth", lambda: (lambda func: func))
    monkeypatch.setattr(app_module.requests, "request", fake_request)

    settings = AppSearchSettings(
        base_url="https://search.example.com",
        token="app-search-token",
        timeout_seconds=30,
        verify_ssl=False,
    )

    app = app_module.create_app(config=settings)
    return app.test_client(), captured_calls


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
def test_proxy_forwards_supported_request_methods(proxy_client, method):
    client, captured_calls = proxy_client

    payload = {"query": method.lower()} if method in {"POST", "PUT", "PATCH"} else None
    response = client.open(
        f"/api/search/{method.lower()}?page=1",
        method=method,
        json=payload,
    )

    assert response.status_code == 200

    outgoing = captured_calls[-1]
    assert outgoing["method"] == method
    assert outgoing["url"] == f"https://search.example.com/api/search/{method.lower()}"
    assert outgoing["params"]["page"] == "1"


def test_proxy_forwards_json_payload(proxy_client):
    client, captured_calls = proxy_client

    payload = {"query": "atlas", "size": 5}
    response = client.post("/api/as/v1/engines/atlas/search.json", json=payload)

    assert response.status_code == 200
    outgoing = captured_calls[-1]
    assert outgoing["data"] == payload
    assert outgoing["headers"]["Content-Type"].startswith("application/json")


def test_proxy_forwards_raw_payload_when_json_parsing_fails(proxy_client):
    client, captured_calls = proxy_client

    response = client.post(
        "/api/as/v1/engines/atlas/search.json",
        data="query=atlas&size=3",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    outgoing = captured_calls[-1]
    assert outgoing["data"] == b"query=atlas&size=3"
    assert outgoing["headers"]["Content-Type"] == "application/x-www-form-urlencoded"


def test_proxy_sets_outgoing_authorization_header_from_settings_token(proxy_client):
    client, captured_calls = proxy_client

    response = client.get(
        "/api/as/v1/engines/atlas/search.json",
        headers={"Authorization": "Bearer user-token-should-not-be-forwarded"},
    )

    assert response.status_code == 200
    outgoing = captured_calls[-1]
    assert outgoing["headers"]["Authorization"] == "Bearer app-search-token"
