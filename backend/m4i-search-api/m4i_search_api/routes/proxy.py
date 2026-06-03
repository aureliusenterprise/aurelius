from typing import Optional

import requests
from flask import Blueprint, Response, request
from werkzeug.datastructures import Headers

from m4i_search_api.providers import AuthProvider, KeyProvider

from ..globals import LOGGER
from ..settings import Settings


def build_target_url(settings: Settings, path: str) -> str:
    """Build the target URL for the App Search instance based on the incoming request path."""
    clean_base = str(settings.base_url).rstrip("/")
    clean_path = path.lstrip("/")

    if not clean_path:
        return clean_base

    return f"{clean_base}/{clean_path}"


FILTERED_HEADERS = {
    "connection",
    "host",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _build_proxy_headers(headers: Headers, api_key: str) -> dict:
    """
    Build headers for the proxied request.

    Filters out hop-by-hop headers per RFC 2616 Section 13.5.1 and replaces the Authorization header with the
    App Search API key.
    """

    result = {k: v for k, v in headers if k.lower() not in FILTERED_HEADERS}
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


def create_proxy_blueprint(
    auth_provider: AuthProvider,
    key_provider: KeyProvider,
    settings: Settings,
) -> Blueprint:
    """Factory that returns a Blueprint wired with the current providers."""
    proxy_bp = Blueprint("proxy", __name__)

    @proxy_bp.route(
        "/",
        defaults={"path": ""},
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @proxy_bp.route(
        "/<path:path>",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )
    @auth_provider.requires_auth()
    def proxy(path: str, access_token: Optional[str] = None) -> Response:  # noqa: F811
        """Proxy endpoint to forward requests to the App Search instance."""
        LOGGER.info("%s %s", request.method, request.path)
        try:
            response = _proxy_request(settings, path, key_provider)
        except Exception:
            LOGGER.exception("Error proxying %s %s", request.method, request.path)
            raise
        else:
            LOGGER.info("%s %s -> %s", request.method, request.path, response.status)
            return response

    return proxy_bp
