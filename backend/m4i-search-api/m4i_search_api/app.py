import logging
from typing import Optional

import requests
from flask import Flask, Response, request
from werkzeug.datastructures import Headers
from m4i_backend_core.shared import register as register_shared

from m4i_search_api.providers import (
    AppSearchKeyProvider,
    AuthProvider,
    KeycloakAuthProvider,
    KeyProvider,
)

from .settings import Settings

LOGGER = logging.getLogger(__name__)


def build_target_url(settings: Settings, path: str) -> str:
    """Build the target URL for the App Search instance based on the incoming request path."""
    clean_base = str(settings.base_url).rstrip("/")
    clean_path = path.lstrip("/")

    if not clean_path:
        return clean_base

    return f"{clean_base}/{clean_path}"


def _build_proxy_headers(headers: Headers, api_key: str) -> dict:
    """
    Build headers for the proxied request.

    Filters out hop-by-hop headers per RFC 2616 Section 13.5.1 and replaces the Authorization header with the
    App Search API key.
    """
    hop_by_hop = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    }

    result = {
        k: v for k, v in headers if k.lower() not in hop_by_hop and k.lower() != "host"
    }

    result["Authorization"] = f"Bearer {api_key}"

    return result


def _proxy_request(
    settings: Settings,
    path: str,
    key_provider: KeyProvider,
) -> Response:
    """Proxy the incoming request to the App Search instance."""
    api_key = key_provider.get_key()
    url = build_target_url(settings, path)

    response = requests.request(
        method=request.method,
        url=url,
        headers=_build_proxy_headers(request.headers, api_key),
        data=request.data,
        params=list(request.args.items(multi=True)),
        timeout=settings.timeout_seconds,
        verify=settings.ca_cert_path.as_posix() if settings.ca_cert_path else False,
    )

    return Response(
        response=response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json"),
    )


def create_routes(
    app: Flask,
    settings: Settings,
    key_provider: KeyProvider,
    auth_provider: AuthProvider,
) -> None:
    """Define the routes for the Flask application."""

    @app.route("/health", methods=["GET"])
    def health() -> Response:
        """Health check endpoint."""
        return Response(None, status=200)

    @app.route(
        "/",
        defaults={"path": ""},
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @app.route(
        "/<path:path>",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @auth_provider.requires_auth()
    def proxy(path: str, access_token: Optional[str] = None) -> Response:
        """Proxy endpoint to forward requests to the App Search instance."""
        return _proxy_request(settings, path, key_provider)


def create_app(
    auth_provider: AuthProvider,
    key_provider: KeyProvider,
    settings: Settings,
) -> Flask:
    """
    Factory function to create and configure the Flask application.

    Args:
        auth_provider: Provider for JWT validation. Defaults to KeycloakAuthProvider.
        key_provider: Provider for the App Search API key. Defaults to AppSearchKeyProvider.
        settings: Application settings. Defaults to loading from environment.
    """
    app = Flask(__name__)

    register_shared(app)
    create_routes(app, settings, key_provider, auth_provider)

    return app


def main() -> Flask:
    """Main entry point for the Flask application."""
    settings = Settings()  # type: ignore[settings are loaded from the environment]

    auth_provider = KeycloakAuthProvider()
    key_provider = AppSearchKeyProvider(settings)

    return create_app(
        auth_provider=auth_provider,
        key_provider=key_provider,
        settings=settings,
    )
