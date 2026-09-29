"""Logging with the tenant of the current request or job.

:data:`tenant_var` holds the tenant id while a request (and every task it starts) runs; tenant contexts set it
while they start, so their background jobs inherit it too.  :class:`TenantFilter` copies it into every log record
(``record.tenant``, ``-`` outside any tenant), :class:`JsonFormatter` writes one JSON object per line - the format
the log shipper reads and routes to the tenant's data stream (``logs-aurelius.pyatlas-<tenant>``; lines without a
tenant go to ``logs-aurelius.pyatlas-platform``).
"""
from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar
from typing import Optional

tenant_var: ContextVar[Optional[str]] = ContextVar("pyatlas_tenant", default=None)

# fields that must never end up in a log line
_SECRET_WORDS = ("authorization", "password", "secret", "token", "cookie", "api_key", "apikey")


class TenantFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "tenant"):
            record.tenant = tenant_var.get() or "-"
        return True


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str = "pyatlas"):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        tenant = getattr(record, "tenant", None) or tenant_var.get() or "-"
        out = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) +
            f".{int(record.msecs):03d}Z",
            "log.level": record.levelname.lower(),
            "log.logger": record.name,
            "message": record.getMessage(),
            "service.name": self.service,
            "tenant": tenant if tenant != "-" else None,
        }
        for key in ("user", "path", "status", "duration_ms", "method", "error_id"):
            v = getattr(record, key, None)
            if v is not None:
                out[key] = v
        if record.exc_info:
            out["error.stack_trace"] = self.formatException(record.exc_info)
            out["error.type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        return json.dumps({k: v for k, v in out.items() if v is not None and not _secret(k)}, ensure_ascii=False,
                          default=str)


def _secret(key: str) -> bool:
    k = key.lower()
    return any(w in k for w in _SECRET_WORDS)


def configure(fmt: str = "text", level: int = logging.INFO) -> None:
    """Root logging: ``text`` (human readable, with the tenant) or ``json`` (one object per line)."""
    handler = logging.StreamHandler()
    handler.addFilter(TenantFilter())
    if (fmt or "text").lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(tenant)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger("elastic_transport").setLevel(logging.WARNING)
