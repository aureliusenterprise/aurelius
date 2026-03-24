import logging
from typing import Optional

import requests
from flask import Flask, Response, jsonify, request
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared

from .settings import AppSearchSettings

log = logging.getLogger(__name__)


def create_app(config: Optional[AppSearchSettings] = None) -> Flask:
    settings = config or AppSearchSettings.from_env()
    app = Flask(__name__)
    app.config["APP_SEARCH_SETTINGS"] = settings

    register_shared(app)

    @app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    @app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    @requires_auth()
    def proxy(path: str, access_token=None):
        return _proxy_request(settings, path)

    return app


def _proxy_request(settings: AppSearchSettings, path: str):
    url = build_target_url(settings.base_url, path)

    payload = request.get_json(silent=True)
    if payload is None and request.data:
        payload = request.data
    elif payload is None:
        payload = {}

    headers = {
        "Authorization": f"Bearer {settings.token}",
        "Content-Type": request.headers.get("Content-Type", "application/json"),
    }

    for header_name in ("X-Request-ID", "X-Correlation-ID", "Host", "X-Forwarded-Proto", "X-Real-IP", "X-Forwarded-For"):
        header_value = request.headers.get(header_name)
        if header_value:
            headers[header_name] = header_value

    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=payload,
            params=request.args,
            timeout=settings.timeout_seconds,
            verify=settings.verify_ssl,
        )
    except requests.RequestException as exc:
        log.exception("Failed to reach backend at %s", url)
        return jsonify(error="search_backend_unavailable", message=str(exc)), 502

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json"),
    )


def build_target_url(base_url: str, path: str) -> str:
    clean_base = base_url.rstrip("/")
    clean_path = path.lstrip("/")
    if not clean_path:
        return clean_base
    return f"{clean_base}/{clean_path}"

