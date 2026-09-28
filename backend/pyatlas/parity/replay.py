"""Check 4 - API responses: recorded frontend requests replayed against pyatlas.

Recordings (``--recording``):

``*.har``
    browser recordings (DevTools > Network > "Save all as HAR with content") of people using the Aurelius
    frontend on the old stack.  The recorded responses are the expected answers, so the old stack does not
    have to be running during the replay.  HAR files contain tokens and cookies: they are never replayed
    (``--token`` / ``--user`` are used instead), but treat the files as secrets.
``*.jsonl``
    one request per line: ``{"method", "path", "body"?, "status"?, "response"?}``.
``*.log``
    Apache httpd access log (common / combined format) of the reverse proxy.  Only GET requests can be
    replayed (the log has no bodies) and there is no recorded response: pass ``--left`` (the old stack) so
    both servers are asked.

Paths are the ones the frontend uses (``/<namespace>/atlas/atlas/v2/...``, ``/<namespace>/atlas/elastic``, ...).
Point ``--right`` at the new reverse proxy and they work unchanged; to call pyatlas directly use
``--rewrite aurelius`` (the proxy's routing table, see ``AURELIUS_REWRITES``) or your own ``--rewrite a=b``.

Writes (POST/PUT/DELETE other than searches) are skipped unless ``--allow-writes``.  Search responses (App
Search ``search.json``) are not diffed field by field: facet counts must be equal and the top-10 result ids
must overlap by at least ``--min-overlap`` (default 0.8).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, urlsplit

from .client import Client
from .diff import Difference, Rules, diff
from .report import Report

ALLOWLIST = Path(__file__).resolve().parent / "allowlists" / "api_responses.json"

# the Aurelius reverse proxy routes (k8s/charts/reverse-proxy/conf.d) mapped onto pyatlas' own paths
AURELIUS_REWRITES: List[Tuple[str, str]] = [
    (r"^/[^/]+/atlas/atlas/", "/api/atlas/"),
    (r"^/[^/]+/atlas2/", "/"),
    (r"^/[^/]+/atlas/elastic/?$", "/api/as/v1/engines/atlas-dev/search.json"),
    (r"^/[^/]+/atlas/data_quality/?$", "/api/as/v1/engines/atlas-dev-quality/search.json"),
    (r"^/[^/]+/atlas/gov_quality/?$", "/api/as/v1/engines/atlas-dev-gov-quality/search.json"),
    (r"^/[^/]+/atlas/lineage_model/?", "/api/aurelius/lineage_model/"),
    (r"^/[^/]+/atlas/api/data_governance_dashboard/?", "/api/aurelius/data_governance_dashboard/"),
    (r"^/[^/]+/atlas/validate_entity/?", "/api/aurelius/validate_entity/"),
]

_SEARCH_PATH = re.compile(r"(/search(\.json)?$)|(/atlas/(elastic|data_quality|gov_quality)/?$)|(/v2/search/)")
_STATIC = re.compile(r"\.(js|css|png|jpg|jpeg|svg|woff2?|ttf|ico|map|html|json\.gz|webmanifest)$|/assets/|/ngsw")


@dataclass
class Recorded:
    method: str
    path: str                       # path + query string
    body: Any = None
    status: Optional[int] = None
    response: Any = None

    @property
    def label(self) -> str:
        return f"{self.method} {self.path}"


# ---------------------------------------------------------------------------------------------- readers
def read_recording(path: str) -> Iterator[Recorded]:
    p = Path(path)
    if p.suffix.lower() == ".har":
        yield from _read_har(p)
    elif p.suffix.lower() == ".jsonl":
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                yield Recorded(d["method"].upper(), d["path"], d.get("body"), d.get("status"), d.get("response"))
    else:
        yield from _read_access_log(p)


def _parse_json(text: Optional[str]) -> Any:
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def _read_har(p: Path) -> Iterator[Recorded]:
    har = json.loads(p.read_text(encoding="utf-8"))
    for e in har.get("log", {}).get("entries", []):
        req, res = e.get("request", {}), e.get("response", {})
        u = urlsplit(req.get("url", ""))
        path = u.path + (f"?{u.query}" if u.query else "")
        content = res.get("content") or {}
        text = content.get("text")
        if text is not None and content.get("encoding") == "base64":
            import base64
            text = base64.b64decode(text).decode("utf-8", "replace")
        mime = (content.get("mimeType") or "").lower()
        if "json" not in mime and not (text or "").lstrip().startswith(("{", "[")):
            continue                            # static files, HTML, images
        yield Recorded(req.get("method", "GET").upper(), path,
                       _parse_json((req.get("postData") or {}).get("text")), res.get("status"), _parse_json(text))


_LOG_LINE = re.compile(r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+" (?P<status>\d{3})')


def _read_access_log(p: Path) -> Iterator[Recorded]:
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _LOG_LINE.search(line)
        if m and m.group("method") == "GET" and not _STATIC.search(m.group("path").split("?")[0]):
            yield Recorded("GET", m.group("path"), status=int(m.group("status")))


# ---------------------------------------------------------------------------------------------- replay
def rewrite(path: str, rules: Sequence[Tuple[str, str]]) -> str:
    for pat, rep in rules:
        new, n = re.subn(pat, rep, path, count=1)
        if n:
            return new
    return path


def _split(path: str) -> Tuple[str, dict]:
    u = urlsplit(path)
    return u.path, dict(parse_qsl(u.query, keep_blank_values=True))


def is_search(r: Recorded) -> bool:
    return bool(_SEARCH_PATH.search(r.path.split("?")[0]))


def result_ids(resp: Any) -> List[str]:
    out = []
    for r in (resp or {}).get("results") or (resp or {}).get("entities") or []:
        rid = r.get("id") if isinstance(r, dict) else None
        if isinstance(rid, dict):
            rid = rid.get("raw")
        out.append(str(rid or r.get("guid")))
    return out


def facets(resp: Any) -> Any:
    return (resp or {}).get("facets")


def compare_search(item: str, expected: Any, got: Any, report: Report, min_overlap: float, top: int = 10) -> float:
    a, b = result_ids(expected)[:top], result_ids(got)[:top]
    overlap = 1.0 if not a and not b else len(set(a) & set(b)) / max(len(a), len(b), 1)
    diffs = diff({"facets": facets(expected), "total": _total(expected)},
                 {"facets": facets(got), "total": _total(got)}, Rules(unordered=["facets.**.data"]))
    if overlap < min_overlap:
        diffs.append(Difference(("top_results_overlap",), f">= {min_overlap}", round(overlap, 3)))
    report.different(item, diffs)
    return overlap


def _total(resp: Any) -> Any:
    meta = (resp or {}).get("meta") or {}
    return ((meta.get("page") or {}).get("total_results")) if meta else (resp or {}).get("approximateCount")


def replay(records: Sequence[Recorded], right: Client, left: Optional[Client] = None,
           rewrites: Sequence[Tuple[str, str]] = (), left_rewrites: Sequence[Tuple[str, str]] = (),
           allow_writes: bool = False, min_overlap: float = 0.8, rules: Optional[Rules] = None,
           report: Optional[Report] = None) -> Report:
    report = report or Report("replay", left.name if left else "recorded responses", right.name)
    rules = rules or Rules.load(ALLOWLIST)
    overlaps: List[float] = []
    skipped = 0
    for r in records:
        search = is_search(r)
        if r.method not in ("GET", "HEAD") and not search and not allow_writes:
            skipped += 1
            continue
        if left is not None:
            lp, lq = _split(rewrite(r.path, left_rewrites))
            exp_status, expected = left.request(r.method, lp, params=lq or None, json=r.body)
        else:
            if r.response is None and r.status is None:
                skipped += 1
                continue
            exp_status, expected = r.status, r.response
        rp, rq = _split(rewrite(r.path, rewrites))
        try:
            status, got = right.request(r.method, rp, params=rq or None, json=r.body)
        except Exception as e:  # noqa: BLE001
            report.error(r.label, str(e))
            continue
        if exp_status is not None and status != exp_status:
            report.different(r.label, diff({"status": exp_status}, {"status": status}))
            continue
        if search and isinstance(expected, dict):
            overlaps.append(compare_search(r.label, expected, got, report, min_overlap))
        else:
            report.different(r.label, diff(expected, got, rules))
    report.stats["requests skipped (writes / no expectation)"] = skipped
    if overlaps:
        report.stats["search requests"] = len(overlaps)
        report.stats["mean top-10 overlap"] = round(sum(overlaps) / len(overlaps), 3)
        report.stats["searches below min overlap"] = sum(1 for o in overlaps if o < min_overlap)
    return report
