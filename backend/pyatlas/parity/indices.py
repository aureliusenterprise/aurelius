"""Check 2 - search and quality indices: App Search engine documents against pyatlas' indices.

Document sets come from (``--left`` / ``--right`` specs):

``file:<path.json>``
    a JSON list of documents, e.g. the golden files ``atlas-dev.json``, ``atlas-dev-quality.json``,
    ``atlas-dev-gov-quality.json`` in ``backend/m4i-atlas-post-install/data`` or a previous ``dump``.
``appsearch:<url>#<engine>``
    all documents of an App Search engine (``documents/list``, private key in ``--appsearch-key`` or
    ``APP_SEARCH_KEY``).
``es:<url>#<index>``
    all documents of an Elasticsearch index (scroll), ``_source`` + ``id`` = ``_id``; user/password from
    ``--es-user`` / ``--es-password`` or ``ES_USER`` / ``ES_PASSWORD``.

Documents are matched by ``id`` and compared field by field with the allow-list (``parity/allowlists``).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from .client import HttpClient, ok
from .diff import Rules, diff
from .report import Report

ALLOWLISTS = Path(__file__).resolve().parent / "allowlists"

# the three Aurelius App Search engines and the allow-list used for each
ENGINES = {"atlas-dev": "search_documents.json", "atlas-dev-quality": "data_quality.json",
           "atlas-dev-gov-quality": "gov_quality.json"}


# ---------------------------------------------------------------------------------------------- loading
def load_documents(spec: str, appsearch_key: Optional[str] = None, es_user: Optional[str] = None,
                   es_password: Optional[str] = None, verify_tls: bool = True) -> List[dict]:
    kind, _, rest = spec.partition(":")
    if kind == "file":
        data = json.loads(Path(rest).read_text(encoding="utf-8"))
        return data["results"] if isinstance(data, dict) and "results" in data else data
    if kind == "appsearch":
        url, _, engine = rest.partition("#")
        return list(app_search_documents(url, engine, appsearch_key or os.environ.get("APP_SEARCH_KEY"),
                                         verify_tls))
    if kind == "es":
        url, _, index = rest.partition("#")
        return list(es_documents(url, index, es_user or os.environ.get("ES_USER"),
                                 es_password or os.environ.get("ES_PASSWORD"), verify_tls))
    raise SystemExit(f"unknown document source {spec!r} (use file:, appsearch: or es:)")


def app_search_documents(url: str, engine: str, key: Optional[str], verify_tls: bool = True,
                         page_size: int = 1000) -> Iterator[dict]:
    if not key:
        raise SystemExit("App Search private key missing (--appsearch-key or APP_SEARCH_KEY)")
    c = HttpClient(url, token=key, name=f"appsearch:{engine}", verify_tls=verify_tls)
    page = 1
    while True:
        body = ok(c, "GET", f"/api/as/v1/engines/{engine}/documents/list",
                  params={"page[current]": page, "page[size]": page_size})
        yield from body.get("results") or []
        if page >= ((body.get("meta") or {}).get("page") or {}).get("total_pages", 0):
            break
        page += 1


def es_documents(url: str, index: str, user: Optional[str] = None, password: Optional[str] = None,
                 verify_tls: bool = True, size: int = 1000) -> Iterator[dict]:
    c = HttpClient(url, user=user, password=password, name=f"es:{index}", verify_tls=verify_tls)
    body = ok(c, "POST", f"/{index}/_search", params={"scroll": "2m"},
              json={"size": size, "sort": ["_doc"], "query": {"match_all": {}}})
    scroll_id = body.get("_scroll_id")
    try:
        while True:
            hits = (body.get("hits") or {}).get("hits") or []
            for h in hits:
                d = dict(h.get("_source") or {})
                d.setdefault("id", h.get("_id"))
                yield d
            if not hits or not scroll_id:
                break
            body = ok(c, "POST", "/_search/scroll", json={"scroll": "2m", "scroll_id": scroll_id})
            scroll_id = body.get("_scroll_id", scroll_id)
    finally:
        if scroll_id:
            c.request("DELETE", "/_search/scroll", json={"scroll_id": [scroll_id]})


def by_id(docs: Iterable[dict], key: str = "id") -> Dict[str, dict]:
    out = {}
    for d in docs:
        k = d.get(key) or d.get("guid")
        if k is not None:
            out[str(k)] = d
    return out


def allowlist_for(engine: Optional[str], path: Optional[str] = None) -> Rules:
    if path:
        return Rules.load(path)
    name = ENGINES.get(engine or "", "search_documents.json")
    return Rules.load(ALLOWLISTS / name)


# ---------------------------------------------------------------------------------------------- check
def compare_documents(left: Iterable[dict], right: Iterable[dict], rules: Optional[Rules] = None,
                      report: Optional[Report] = None, left_name: str = "left", right_name: str = "right",
                      key: str = "id") -> Report:
    report = report or Report("indices", left_name, right_name)
    rules = rules or Rules()
    a, b = by_id(left, key), by_id(right, key)
    for k in sorted(a):
        if k not in b:
            report.missing(k, f"{a[k].get('typename')} {a[k].get('name')}")
            continue
        report.different(k, diff(a[k], b[k], rules))
    for k in sorted(set(b) - set(a)):
        report.extra(k, f"{b[k].get('typename')} {b[k].get('name')}")
    report.stats.update({"documents left": len(a), "documents right": len(b),
                         "matched": len(set(a) & set(b))})
    return report
