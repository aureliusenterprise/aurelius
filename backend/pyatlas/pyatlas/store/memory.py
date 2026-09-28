"""A small in-memory stand-in for ``AsyncElasticsearch`` (development / demo / tests only).

Start the server with ``python -m pyatlas --in-memory`` to try pyatlas without an
Elasticsearch cluster.  Data is lost on restart.

It implements just enough of the document and query APIs used by pyatlas
(get/mget/index/delete/bulk/search/count/delete_by_query and the query DSL
subset built by the repository and discovery layers) to run the full service
in unit tests without an Elasticsearch cluster.  It is *not* a faithful
Elasticsearch emulation: scoring is naive and analysers are approximated.
"""
from __future__ import annotations

import copy
import fnmatch
import re
from typing import Any, Dict, List, Optional

from elasticsearch import ConflictError, NotFoundError


class _Meta:
    def __init__(self, status):
        self.status = status


def _not_found(msg="not found"):
    return NotFoundError(msg, _Meta(404), {"found": False})


def _conflict(msg="version conflict"):
    return ConflictError(msg, _Meta(409), {"error": {"type": "version_conflict_engine_exception"}})


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokens(text: str) -> List[str]:
    out: List[str] = []
    for part in re.split(r"\s+", str(text)):
        if not part:
            continue
        out.append(part.lower())
        for t in _TOKEN_RE.findall(part):
            out.append(t.lower())
            # split on case change like word_delimiter_graph
            for sub in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", t):
                out.append(sub.lower())
    return out


def _get_path(src: Any, path: str) -> List[Any]:
    """Return list of values found at dotted path (flattening arrays)."""
    cur = [src]
    for part in path.split("."):
        nxt = []
        for c in cur:
            if isinstance(c, list):
                for x in c:
                    if isinstance(x, dict) and part in x:
                        nxt.append(x[part])
            elif isinstance(c, dict) and part in c:
                nxt.append(c[part])
        cur = nxt
    out = []
    for c in cur:
        if isinstance(c, list):
            out.extend(c)
        else:
            out.append(c)
    return [v for v in out if v is not None]


def _field_values(src: dict, field: str):
    """Return (values, mode) where mode is 'kw', 'lc' or 'text'."""
    if field.endswith(".lc"):
        return [str(v).lower() for v in _get_path(src, field[:-3])], "lc"
    if field.endswith(".text"):
        return _get_path(src, field[:-5]), "text"
    if field == "fulltext" or field.endswith("fulltext"):
        return _get_path(src, field), "text"
    return _get_path(src, field), "kw"


def _cmp_eq(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == (b if isinstance(b, bool) else str(b).lower() == "true")
    if isinstance(a, (int, float)) and not isinstance(b, (int, float)):
        try:
            return float(a) == float(b)
        except (TypeError, ValueError):
            return False
    return a == b


class FakeIndices:
    def __init__(self, es: "FakeElasticsearch"):
        self.es = es

    async def exists(self, index: str) -> bool:
        return index in self.es.data

    async def create(self, index: str, **kwargs):
        self.es.data.setdefault(index, {})
        return {"acknowledged": True}

    async def put_mapping(self, index: str, **kwargs):
        return {"acknowledged": True}

    async def delete(self, index: str, ignore_unavailable: bool = False, **kwargs):
        for i in index.split(","):
            self.es.data.pop(i, None)
        return {"acknowledged": True}

    async def refresh(self, index: str = None, **kwargs):
        return {}


class FakeElasticsearch:
    def __init__(self):
        self.data: Dict[str, Dict[str, dict]] = {}
        self.seq = 0
        self.indices = FakeIndices(self)

    async def close(self):
        pass

    def _idx(self, index: str) -> Dict[str, dict]:
        return self.data.setdefault(index, {})

    # ------------------------------------------------------------- documents
    async def get(self, index: str, id: str, **kw):
        d = self._idx(index).get(id)
        if d is None:
            raise _not_found()
        return {"_id": id, "_source": copy.deepcopy(d["src"]), "_seq_no": d["seq"], "_primary_term": 1, "found": True}

    async def mget(self, index: str, ids: List[str], **kw):
        docs = []
        for i in ids:
            d = self._idx(index).get(i)
            if d is None:
                docs.append({"_id": i, "found": False})
            else:
                docs.append({"_id": i, "found": True, "_source": copy.deepcopy(d["src"]), "_seq_no": d["seq"],
                             "_primary_term": 1})
        return {"docs": docs}

    def _write(self, index, id, doc, op_type=None, if_seq_no=None):
        idx = self._idx(index)
        if op_type == "create" and id in idx:
            raise _conflict()
        if if_seq_no is not None:
            cur = idx.get(id)
            if cur is None or cur["seq"] != if_seq_no:
                raise _conflict()
        self.seq += 1
        idx[id] = {"src": copy.deepcopy(doc), "seq": self.seq}

    async def index(self, index: str, id: str, document: dict, op_type: str = None, refresh=None, **kw):
        self._write(index, id, document, op_type)
        return {"_id": id, "result": "created"}

    async def delete(self, index: str, id: str, refresh=None, **kw):
        if id not in self._idx(index):
            raise _not_found()
        del self._idx(index)[id]
        return {"result": "deleted"}

    async def bulk(self, operations: List[dict], refresh=None, **kw):
        items = []
        i = 0
        while i < len(operations):
            (op, meta), = operations[i].items()
            i += 1
            doc = None
            if op != "delete":
                doc = operations[i]
                i += 1
            try:
                if op == "delete":
                    if meta["_id"] not in self._idx(meta["_index"]):
                        items.append({op: {"_id": meta["_id"], "status": 404, "error": {"type": "not_found"}}})
                        continue
                    del self._idx(meta["_index"])[meta["_id"]]
                else:
                    self._write(meta["_index"], meta["_id"], doc, "create" if op == "create" else None,
                                meta.get("if_seq_no"))
                items.append({op: {"_id": meta["_id"], "status": 200}})
            except ConflictError:
                items.append({op: {"_id": meta["_id"], "status": 409, "error": {"type": "version_conflict_engine_exception"}}})
        return {"items": items, "errors": any("error" in list(x.values())[0] for x in items)}

    # ------------------------------------------------------------- search
    def _hits(self, index: str, query: dict):
        out = []
        for i in index.split(","):
            for _id, d in self._idx(i).items():
                ok, score = self._match(d["src"], query or {"match_all": {}})
                if ok:
                    out.append((_id, d["src"], score))
        return out

    async def search(self, index: str, query: dict = None, size: int = 10, from_: int = 0, sort=None, source=True,
                     aggs=None, track_total_hits=True, search_after=None, **kw):
        hits = self._hits(index, query)
        sort_spec = self._norm_sort(sort)
        hits = self._sort(hits, sort_spec)
        total = len(hits)
        if search_after is not None:
            hits = [h for h in hits if self._sort_key_values(h, sort_spec) > list(search_after)]
        page = hits[from_:from_ + size] if size else []
        res_hits = []
        for _id, src, score in page:
            h = {"_id": _id, "_score": score, "_source": self._filter_source(src, source)}
            if sort_spec:
                h["sort"] = self._sort_key_values((_id, src, score), sort_spec)
            res_hits.append(h)
        resp = {"hits": {"total": {"value": total, "relation": "eq"}, "hits": res_hits}}
        if aggs:
            resp["aggregations"] = {}
            for name, spec in aggs.items():
                if "terms" in spec:
                    field = spec["terms"]["field"]
                    counts: Dict[Any, int] = {}
                    for _id, src, _ in hits:
                        for v in set(map(str, _get_path(src, field))):
                            counts[v] = counts.get(v, 0) + 1
                    buckets = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[: spec["terms"].get("size", 10)]
                    resp["aggregations"][name] = {"buckets": [{"key": k, "doc_count": c} for k, c in buckets]}
        return resp

    async def count(self, index: str, query: dict = None, **kw):
        return {"count": len(self._hits(index, query))}

    async def delete_by_query(self, index: str, query: dict, **kw):
        n = 0
        for i in index.split(","):
            for _id, src, _ in list(self._hits(i, query)):
                del self._idx(i)[_id]
                n += 1
        return {"deleted": n}

    @staticmethod
    def _filter_source(src, source):
        if source is True or source is None:
            return copy.deepcopy(src)
        if source is False:
            return {}
        includes = source if isinstance(source, list) else source.get("includes", [])
        if not includes:
            return copy.deepcopy(src)
        return {k: copy.deepcopy(v) for k, v in src.items() if k in includes}

    @staticmethod
    def _norm_sort(sort):
        out = []
        for s in sort or []:
            if isinstance(s, str):
                out.append((s, "asc" if s != "_score" else "desc"))
            else:
                (f, spec), = s.items()
                order = spec if isinstance(spec, str) else spec.get("order", "asc")
                out.append((f, order))
        return out

    @staticmethod
    def _sort_key_values(hit, spec):
        _id, src, score = hit
        vals = []
        for f, _ in spec:
            if f == "_score":
                vals.append(score)
            elif f == "_id":
                vals.append(_id)
            else:
                v, _ = _field_values(src, f)
                vals.append(v[0] if v else None)
        return vals

    def _sort(self, hits, spec):
        if not spec:
            return sorted(hits, key=lambda h: -h[2])
        for f, order in reversed(spec):
            rev = order == "desc"
            present = [h for h in hits if self._sort_key_values(h, [(f, order)])[0] is not None]
            missing = [h for h in hits if self._sort_key_values(h, [(f, order)])[0] is None]
            present.sort(key=lambda h: _sortable(self._sort_key_values(h, [(f, order)])[0]), reverse=rev)
            hits = present + missing
        return hits

    # ------------------------------------------------------------- query DSL
    def _match(self, src: dict, q: dict):
        (kind, body), = q.items()
        if kind == "match_all":
            return True, 1.0
        if kind == "match_none":
            return False, 0.0
        if kind == "bool":
            score = 0.0
            for c in _as_list(body.get("must")) + _as_list(body.get("filter")):
                ok, s = self._match(src, c)
                if not ok:
                    return False, 0.0
                score += s
            for c in _as_list(body.get("must_not")):
                if self._match(src, c)[0]:
                    return False, 0.0
            shoulds = _as_list(body.get("should"))
            if shoulds:
                matched = [self._match(src, c) for c in shoulds]
                n = sum(1 for ok, _ in matched if ok)
                msm = body.get("minimum_should_match")
                if msm is None:
                    msm = 0 if (body.get("must") or body.get("filter")) else 1
                if n < int(msm):
                    return False, 0.0
                score += sum(s for ok, s in matched if ok)
            return True, score or 1.0
        if kind == "ids":
            return src.get("guid") in body["values"] or False, 1.0
        if kind == "term":
            (field, v), = body.items()
            if isinstance(v, dict):
                v = v.get("value")
            vals, mode = _field_values(src, field)
            if mode == "lc":
                v = str(v).lower()
            return any(_cmp_eq(x, v) for x in vals), 1.0
        if kind == "terms":
            (field, vs), = [(k, v) for k, v in body.items() if k != "boost"]
            vals, mode = _field_values(src, field)
            if mode == "lc":
                vs = [str(x).lower() for x in vs]
            return any(_cmp_eq(x, v) for x in vals for v in vs), 1.0
        if kind == "exists":
            vals, _ = _field_values(src, body["field"])
            return len(vals) > 0, 1.0
        if kind == "range":
            (field, cond), = body.items()
            vals, _ = _field_values(src, field)
            for x in vals:
                try:
                    ok = True
                    for op, lim in cond.items():
                        if op == "gt" and not x > lim: ok = False
                        if op == "gte" and not x >= lim: ok = False
                        if op == "lt" and not x < lim: ok = False
                        if op == "lte" and not x <= lim: ok = False
                    if ok:
                        return True, 1.0
                except TypeError:
                    continue
            return False, 0.0
        if kind in ("prefix", "wildcard"):
            (field, spec), = body.items()
            v = spec["value"] if isinstance(spec, dict) else spec
            ci = isinstance(spec, dict) and spec.get("case_insensitive")
            vals, mode = _field_values(src, field)
            pattern = v + "*" if kind == "prefix" else v
            for x in vals:
                xs = str(x)
                if mode == "lc" or ci:
                    xs, p = xs.lower(), pattern.lower()
                else:
                    p = pattern
                if fnmatch.fnmatchcase(xs, p):
                    return True, 1.0
            return False, 0.0
        if kind == "nested":
            path = body["path"]
            items = src.get(path) or []
            for it in items:
                ok, s = self._match({path: it}, body["query"])
                if ok:
                    return True, s
            return False, 0.0
        if kind in ("simple_query_string", "query_string", "multi_match"):
            text = body["query"]
            fields = body.get("fields") or ["fulltext"]
            q_tokens = [t for t in re.split(r"[\s]+", text.lower()) if t and t not in ("and", "or", "+", "|")]
            if not q_tokens:
                return True, 1.0
            doc_tokens = set()
            for f in fields:
                f = f.split("^")[0]
                if "*" in f:
                    for path in _expand_wild(src, f):
                        for v in _get_path(src, path):
                            doc_tokens.update(_tokens(v))
                else:
                    vals, _ = _field_values(src, f)
                    for v in vals:
                        doc_tokens.update(_tokens(v))
            score = 0.0
            for qt in q_tokens:
                qt = qt.strip('"')
                if qt.endswith("*"):
                    hit = any(t.startswith(qt[:-1]) for t in doc_tokens)
                else:
                    sub = _tokens(qt)
                    hit = all(any(t == s for t in doc_tokens) for s in sub[:1]) if sub else True
                if not hit:
                    return False, 0.0
                score += 1.0
            return True, score
        raise NotImplementedError(f"fake es: unsupported query {kind}")


def _expand_wild(src: dict, pattern: str) -> List[str]:
    base = pattern[:-5] if pattern.endswith(".text") else pattern
    paths = []

    def walk(obj, prefix):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{prefix}.{k}" if prefix else k)
        else:
            paths.append(prefix)
    walk(src, "")
    return [p for p in paths if fnmatch.fnmatchcase(p, base)]


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _sortable(v):
    if isinstance(v, bool):
        return (0, int(v))
    if isinstance(v, (int, float)):
        return (0, v)
    return (1, str(v))
