"""Thin async wrapper around the Elasticsearch client.

Everything that talks to Elasticsearch goes through :class:`EsStore`, which keeps
index naming, refresh policy and paging in one place.
"""
from __future__ import annotations

import contextlib
from contextvars import ContextVar

import logging
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional, Tuple

from elasticsearch import AsyncElasticsearch, ConflictError, NotFoundError

from ..config import Settings
from .mappings import ANALYSIS, INDICES

log = logging.getLogger(__name__)

__all__ = ["EsStore", "ConflictError", "NotFoundError", "make_client"]


def make_client(settings: Settings) -> AsyncElasticsearch:
    kwargs: Dict[str, Any] = {"hosts": settings.es_host_list, "request_timeout": 60}
    if settings.es_api_key:
        kwargs["api_key"] = settings.es_api_key
    elif settings.es_username:
        kwargs["basic_auth"] = (settings.es_username, settings.es_password or "")
    if settings.es_ca_certs:
        kwargs["ca_certs"] = settings.es_ca_certs
    if not settings.es_verify_certs:
        kwargs["verify_certs"] = False
    return AsyncElasticsearch(**kwargs)



# Bulk operations (imports) use "deferred refresh": writes do not wait for a refresh (the default
# "wait_for" waits for the next periodic refresh, up to index.refresh_interval = 1s per write); instead
# the written indices are remembered and refreshed right before the next search on them, so reads in
# the same operation still see all writes (get/mget are real-time anyway).
_dirty: ContextVar[Optional[set]] = ContextVar("pyatlas_dirty_indices", default=None)

class EsStore:
    def __init__(self, client: AsyncElasticsearch, settings: Settings):
        self.es = client
        self.settings = settings
        self.prefix = settings.es_index_prefix
        self.refresh = settings.es_refresh
        # callables(index) told about every write (e.g. the Aurelius search documents follow entity changes)
        self.listeners: List[Any] = []

    def _notify(self, *indices: str) -> None:
        for fn in self.listeners:
            for idx in indices:
                try:
                    fn(idx)
                except Exception:  # pragma: no cover - a listener must never break a write
                    log.exception("write listener failed")

    # ------------------------------------------------------------------ indices
    def index(self, name: str) -> str:
        return f"{self.prefix}_{name}"

    @property
    def entities(self) -> str:
        return self.index("entities")

    @property
    def relationships(self) -> str:
        return self.index("relationships")

    @property
    def typedefs(self) -> str:
        return self.index("typedefs")

    @property
    def unique(self) -> str:
        return self.index("unique")

    @property
    def audit(self) -> str:
        return self.index("audit")

    @property
    def meta(self) -> str:
        return self.index("meta")

    @property
    def access(self) -> str:
        return self.index("access")

    async def bootstrap(self) -> None:
        """Create the indices if they do not exist yet."""
        for name, mapping in INDICES.items():
            idx = self.index(name)
            if await self.es.indices.exists(index=idx):
                # keep mappings up to date with additive changes
                try:
                    await self.es.indices.put_mapping(index=idx, **_mapping_body(mapping))
                except Exception as e:  # pragma: no cover - informational only
                    log.warning("could not update mapping of %s: %s", idx, e)
                continue
            log.info("creating index %s", idx)
            await self.es.indices.create(
                index=idx,
                settings={
                    "number_of_shards": self.settings.es_shards,
                    "number_of_replicas": self.settings.es_replicas,
                    "analysis": ANALYSIS,
                    "mapping": {"total_fields": {"limit": 20000}},
                },
                mappings=mapping,
            )

    async def drop_all(self) -> None:
        for name in INDICES:
            await self.es.indices.delete(index=self.index(name), ignore_unavailable=True)

    async def refresh_all(self) -> None:
        await self.es.indices.refresh(index=",".join(self.index(n) for n in INDICES))

    # ------------------------------------------------------------------ refresh handling
    def _write_refresh(self, explicit: Optional[str], *indices: str):
        dirty = _dirty.get()
        if dirty is not None:
            dirty.update(indices)
            return explicit or "false"
        return explicit or self.refresh

    async def _before_search(self, index: str) -> None:
        dirty = _dirty.get()
        if dirty:
            hit = [i for i in index.split(",") if i in dirty]
            if hit:
                await self.es.indices.refresh(index=",".join(hit))
                dirty.difference_update(hit)

    @contextlib.asynccontextmanager
    async def deferred_refresh(self):
        """Bulk mode: refresh lazily (see module comment) and refresh everything written at the end."""
        if _dirty.get() is not None:      # nested: the outer block handles it
            yield
            return
        dirty: set = set()
        tok = _dirty.set(dirty)
        try:
            yield
        finally:
            _dirty.reset(tok)
            if dirty:
                await self.es.indices.refresh(index=",".join(sorted(dirty)))

    # ------------------------------------------------------------------ docs
    async def get(self, index: str, doc_id: str, with_version: bool = False) -> Optional[dict]:
        try:
            r = await self.es.get(index=index, id=doc_id)
        except NotFoundError:
            return None
        src = r["_source"]
        if with_version:
            src = dict(src)
            src["_seq_no"] = r.get("_seq_no")
            src["_primary_term"] = r.get("_primary_term")
        return src

    async def mget(self, index: str, ids: Iterable[str], with_version: bool = False,
                   source_includes: Optional[List[str]] = None) -> Dict[str, dict]:
        ids = [i for i in dict.fromkeys(ids) if i]
        out: Dict[str, dict] = {}
        for chunk in _chunks(ids, 1000):
            kwargs = {"source_includes": source_includes} if source_includes else {}
            r = await self.es.mget(index=index, ids=chunk, **kwargs)
            for d in r["docs"]:
                if d.get("found"):
                    src = d["_source"]
                    if with_version:
                        src = dict(src)
                        src["_seq_no"] = d.get("_seq_no")
                        src["_primary_term"] = d.get("_primary_term")
                    out[d["_id"]] = src
        return out

    async def put(self, index: str, doc_id: str, doc: dict, create: bool = False, refresh: Optional[str] = None) -> None:
        kwargs = {}
        if create:
            kwargs["op_type"] = "create"
        await self.es.index(index=index, id=doc_id, document=doc, refresh=self._write_refresh(refresh, index), **kwargs)
        self._notify(index)

    async def delete(self, index: str, doc_id: str, refresh: Optional[str] = None) -> bool:
        try:
            await self.es.delete(index=index, id=doc_id, refresh=self._write_refresh(refresh, index))
            self._notify(index)
            return True
        except NotFoundError:
            return False

    async def bulk(self, actions: List[dict], refresh: Optional[str] = None) -> List[dict]:
        """Execute bulk actions.

        ``actions`` is a list of ``{"op": "index"|"create"|"delete", "index": ..., "id": ...,
        "doc": {...}, "if_seq_no": .., "if_primary_term": ..}``. Returns the per-item
        results; raises nothing for per-item failures (caller inspects them).
        """
        if not actions:
            return []
        results: List[dict] = []
        for chunk in _chunks(actions, 500):
            ops: List[dict] = []
            for a in chunk:
                meta = {"_index": a["index"], "_id": a["id"]}
                if a.get("if_seq_no") is not None:
                    meta["if_seq_no"] = a["if_seq_no"]
                    meta["if_primary_term"] = a["if_primary_term"]
                ops.append({a["op"]: meta})
                if a["op"] != "delete":
                    ops.append(a["doc"])
            r = await self.es.bulk(operations=ops, refresh=self._write_refresh(refresh, *{a["index"] for a in chunk}))
            self._notify(*{a["index"] for a in chunk})
            for item in r["items"]:
                (op, res), = item.items()
                results.append({"op": op, "id": res.get("_id"), "status": res.get("status"), "error": res.get("error")})
        return results

    # ------------------------------------------------------------------ search
    async def search(self, index: str, query: dict, size: int = 10, from_: int = 0, sort: Optional[list] = None,
                     source: Any = True, aggs: Optional[dict] = None, track_total_hits: Any = True) -> dict:
        body: Dict[str, Any] = {"query": query, "size": size, "from_": from_, "track_total_hits": track_total_hits}
        if sort:
            body["sort"] = sort
        if source is not True:
            body["source"] = source
        if aggs:
            body["aggs"] = aggs
        await self._before_search(index)
        return await self.es.search(index=index, **body)

    async def count(self, index: str, query: dict) -> int:
        await self._before_search(index)
        r = await self.es.count(index=index, query=query)
        return int(r["count"])

    async def scan(self, index: str, query: dict, page: int = 1000, sort_field: str = "_id",
                   source: Any = True, limit: Optional[int] = None) -> AsyncIterator[Tuple[str, dict]]:
        """Iterate over all matching docs using search_after on a keyword field."""
        after = None
        seen = 0
        sort_key = "guid" if sort_field == "_id" else sort_field
        while True:
            body: Dict[str, Any] = {"query": query, "size": page, "sort": [{sort_key: "asc"}], "track_total_hits": False}
            if source is not True:
                body["source"] = source
            if after is not None:
                body["search_after"] = after
            await self._before_search(index)
            r = await self.es.search(index=index, **body)
            hits = r["hits"]["hits"]
            if not hits:
                return
            for h in hits:
                yield h["_id"], h.get("_source", {})
                seen += 1
                if limit is not None and seen >= limit:
                    return
            after = hits[-1]["sort"]
            if len(hits) < page:
                return

    async def delete_by_query(self, index: str, query: dict) -> int:
        await self._before_search(index)
        r = await self.es.delete_by_query(index=index, query=query, refresh=True, conflicts="proceed")
        self._notify(*index.split(","))
        return int(r.get("deleted", 0))


def _chunks(seq: List[Any], n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _mapping_body(mapping: dict) -> dict:
    body = {"properties": mapping.get("properties", {})}
    if "dynamic_templates" in mapping:
        body["dynamic_templates"] = mapping["dynamic_templates"]
    return body
