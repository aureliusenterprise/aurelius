import logging
from functools import lru_cache
from typing import Optional

import requests
from flask import Flask, Response, request
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared
from requests.auth import HTTPBasicAuth

from .settings import Settings

log = logging.getLogger(__name__)


def build_target_url(settings: Settings, path: str) -> str:
    """Build the target URL for the App Search instance based on the incoming request path."""
    clean_base = str(settings.base_url).rstrip("/")
    clean_path = path.lstrip("/")

    if not clean_path:
        return clean_base

    return f"{clean_base}/{clean_path}"


@lru_cache()
def get_enterprise_search_key(settings: Settings) -> str:
    """Get the enterprise search key for the App Search instance."""
    clean_base = str(settings.base_url).rstrip("/")

    key_response = requests.get(
        f"{clean_base}/api/as/v1/credentials/private-key",
        auth=HTTPBasicAuth(settings.username, settings.password.get_secret_value()),
    )

    key_info = key_response.json()

    return key_info["key"]


def _proxy_request(settings: Settings, path: str):
    """Proxy the incoming request to the App Search instance."""
    url = build_target_url(settings, path)

    token = get_enterprise_search_key(settings)

    headers = {
        **request.headers,
        "Authorization": f"Bearer {token}",
    }

    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.data,
        timeout=settings.timeout_seconds,
        verify=settings.verify_ssl,
    )

    return Response(
        response=response.content,
        status=response.status_code,
        headers=response.headers,
    )


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()  # type: ignore[settings are loaded from the environment]


def create_routes(app: Flask, settings: Settings) -> None:
    """Define the routes for the Flask application."""

    @app.route(
        "/",
        defaults={"path": ""},
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @app.route(
        "/<path:path>",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @requires_auth()
    def proxy(path: str, access_token: Optional[str] = None):
        return _proxy_request(settings, path)


def create_app(settings: Settings) -> Flask:
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)

    register_shared(app)
    create_routes(app, settings)

    return app


def main() -> Flask:
    """Main entry point for the Flask application."""
    settings = get_settings()
    app = create_app(settings)
    return app
