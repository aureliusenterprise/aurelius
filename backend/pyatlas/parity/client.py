"""Minimal HTTP client for the Atlas v2 REST API, used against both Apache Atlas and pyatlas.

Only the standard library is used so the parity tools run anywhere (``python -m parity ...``).  A client is
anything with ``request(method, path, params=None, json=None) -> (status, body)``; the tests pass an adapter
around FastAPI's TestClient instead of :class:`HttpClient`.
"""
from __future__ import annotations

import base64
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Protocol, Tuple


class Client(Protocol):
    name: str

    def request(self, method: str, path: str, params: Optional[dict] = None, json: Any = None,
                headers: Optional[dict] = None) -> Tuple[int, Any]: ...


class HttpClient:
    """``base_url`` is the server root, e.g. ``http://localhost:21000`` (pyatlas) or ``http://atlas:21000``.

    Authentication: ``user``/``password`` (HTTP Basic, file users) or ``token`` (a Keycloak bearer token).
    ``api_prefix`` is prepended to paths starting with ``/api/atlas`` when the server sits behind the Aurelius
    reverse proxy (e.g. ``/<namespace>/atlas/atlas`` maps to Atlas' ``/api/atlas``).
    """

    def __init__(self, base_url: str, user: Optional[str] = None, password: Optional[str] = None,
                 token: Optional[str] = None, name: Optional[str] = None, verify_tls: bool = True,
                 timeout: float = 120.0, api_prefix: Optional[str] = None, retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.name = name or self.base_url
        self.headers: Dict[str, str] = {"Accept": "application/json", "User-Agent": "aurelius-parity/1.0"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        elif user is not None:
            raw = f"{user}:{password or ''}".encode("utf-8")
            self.headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
        self.ctx = None if verify_tls else ssl._create_unverified_context()  # noqa: S323 - opt-in for test servers
        self.timeout = timeout
        self.api_prefix = api_prefix.rstrip("/") if api_prefix else None
        self.retries = retries

    def url(self, path: str, params: Optional[dict] = None) -> str:
        if self.api_prefix and path.startswith("/api/atlas"):
            path = self.api_prefix + path[len("/api/atlas"):]
        u = self.base_url + path
        if params:
            u += "?" + urllib.parse.urlencode(params, doseq=True)
        return u

    def request(self, method: str, path: str, params: Optional[dict] = None, json: Any = None,  # noqa: A002
                headers: Optional[dict] = None, raw_body: Optional[bytes] = None) -> Tuple[int, Any]:
        h = dict(self.headers)
        h.update(headers or {})
        data = raw_body
        if json is not None:
            data = _json.dumps(json).encode("utf-8")
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(self.url(path, params), data=data, method=method.upper(), headers=h)
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout, context=self.ctx) as r:  # noqa: S310
                    return r.status, _decode(r.read())
            except urllib.error.HTTPError as e:
                return e.code, _decode(e.read())
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt >= self.retries:
                    raise
                time.sleep(1 + attempt)
        raise RuntimeError("unreachable")


_json = json


def _decode(body: bytes) -> Any:
    if not body:
        return None
    try:
        return _json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return body.decode("utf-8", "replace")


def ok(client: Client, method: str, path: str, **kw) -> Any:
    """``request`` that raises on a non-2xx status."""
    status, body = client.request(method, path, **kw)
    if status // 100 != 2:
        raise RuntimeError(f"{client.name}: {method} {path} -> {status}: {str(body)[:500]}")
    return body
