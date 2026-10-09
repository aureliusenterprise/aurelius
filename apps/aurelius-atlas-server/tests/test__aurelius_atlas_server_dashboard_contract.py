"""The dashboard image forwards the API to this server: its nginx configuration must agree with the app."""

import re
from pathlib import Path

import pytest
from aurelius_atlas_server.app import API_PREFIX
from aurelius_atlas_server.settings import ServerSettings

DASHBOARD = Path(__file__).resolve().parents[2] / "aurelius-atlas-dashboard"


@pytest.mark.covers("aurelius_atlas_server.app.create_app", rules=["DSH-02"])
def test__dashboard_proxies_api_to_server_port() -> None:
    """Nginx forwards /api/ to the server's default port, and the API lives under /api/."""
    nginx = (DASHBOARD / "nginx.conf").read_text(encoding="utf-8")
    port = ServerSettings.model_fields["port"].default

    assert API_PREFIX.startswith("/api/")
    assert re.search(r"location /api/ \{\s*proxy_pass http://aurelius_atlas_server;", nginx)
    assert f"server aurelius-atlas-server:{port};" in nginx


@pytest.mark.covers("aurelius_atlas_server.app.create_app", rules=["DSH-01"])
def test__dashboard_serves_both_uis_at_atlas_paths() -> None:
    """dashboardv2 is copied to the web root and dashboardv3 to /n/, from the pinned Atlas commit."""
    dockerfile = (DASHBOARD / "Dockerfile").read_text(encoding="utf-8")

    assert "/src/dashboardv2/dist /usr/share/nginx/html\n" in dockerfile
    assert "/src/dashboardv3/dist/n /usr/share/nginx/html/n\n" in dockerfile
    assert "ARG ATLAS_COMMIT=4787b753271718d0b06cf6545f331f9a12ce1f63" in dockerfile
    assert 'test "$(git rev-parse HEAD)" = "${ATLAS_COMMIT}"' in dockerfile
