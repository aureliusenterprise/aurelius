"""Keeps the Aurelius search indices in step with the metadata (replaces the Flink jobs + Kafka Connect).

* ``<prefix>_aurelius_atlas_dev``              search documents (:mod:`.search_docs`), rebuilt from the graph
* ``<prefix>_aurelius_atlas_dev_quality``      data quality results (:mod:`.data_quality`; posted by quality
                                               tooling, metadata refreshed from the graph)
* ``<prefix>_aurelius_atlas_dev_gov_quality``  governance quality results (:mod:`.gov_quality`), computed

Every write to the entity or relationship index marks the documents stale; a background task rebuilds them
shortly after the writes stop (debounced), so imports and bulk edits cause one rebuild.  Changed documents are
written, vanished ones deleted.  ``POST /api/aurelius/admin/search/rebuild`` forces a rebuild.

A full rebuild reads every Aurelius entity and relationship once; this is fine up to some 100,000 entities.
Incremental recomputation of the affected neighbourhood (:func:`.search_docs.affected_guids`) is the next step
for larger installations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from ..repository.converter import entity_to_api
from . import data_quality
from .engines import DATA_QUALITY, ENGINES, GOV_QUALITY, SEARCH_DOCUMENTS, index_suffix, mapping
from .gov_quality import build_gov_documents, load_rules
from .search_docs import DOCUMENT_TYPES, build_documents

log = logging.getLogger("pyatlas.aurelius")

# entity types read for a rebuild (document types + sources, which are blacklisted but related)
READ_TYPES = sorted(DOCUMENT_TYPES | {"m4i_source"})


class AureliusService:
    def __init__(self, services, debounce_secs: float = 1.0, max_delay_secs: float = 10.0,
                 gov_rules_dir: Optional[str] = None):
        self.s = services
        self.gov_rules = load_rules(gov_rules_dir)
        self.store = services.store
        self.debounce = debounce_secs
        self.max_delay = max_delay_secs
        self._dirty_since: Optional[float] = None
        self._last_write = 0.0
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.last_rebuild: Dict = {}
        self.enabled_listener = True
        self.store.listeners.append(self._on_write)

    # ------------------------------------------------------------------ indices
    def index(self, engine: str) -> str:
        return self.store.index(index_suffix(engine))

    async def bootstrap(self) -> None:
        from ..store.mappings import ANALYSIS
        for engine in ENGINES:
            idx = self.index(engine)
            if await self.store.es.indices.exists(index=idx):
                continue
            log.info("creating index %s", idx)
            await self.store.es.indices.create(index=idx, settings={
                "number_of_shards": self.s.settings.es_shards, "number_of_replicas": self.s.settings.es_replicas,
                "analysis": ANALYSIS}, mappings=mapping(engine))

    async def seed_quality(self, files: str) -> None:
        """Load quality result documents (JSON lists like ``atlas-dev-quality.json``) into empty indices."""
        for raw in (p.strip() for p in (files or "").split(",")):
            if not raw:
                continue
            path = Path(raw)
            if "gov" in path.name:
                log.info("ignoring %s: governance quality is computed from the metadata", path.name)
                continue
            engine = DATA_QUALITY
            if not path.is_file():
                log.warning("quality seed %s not found", path)
                continue
            idx = self.index(engine)
            if await self.store.count(idx, {"match_all": {}}) > 0:
                continue
            docs = json.loads(path.read_text(encoding="utf-8"))
            await self.store.bulk([{"op": "index", "index": idx, "id": str(d["id"]), "doc": d} for d in docs],
                                  refresh="true")
            log.info("seeded %d %s documents from %s", len(docs), engine, path.name)

    # ------------------------------------------------------------------ change tracking
    def _on_write(self, index: str) -> None:
        if not self.enabled_listener or index not in (self.store.entities, self.store.relationships):
            return
        self.mark_stale()

    def mark_stale(self) -> None:
        """Schedule a (debounced) rebuild."""
        now = time.monotonic()
        self._last_write = now
        if self._dirty_since is None:
            self._dirty_since = now
        if self._task is None or self._task.done():
            try:
                self._task = asyncio.get_running_loop().create_task(self._debounced())
            except RuntimeError:          # no loop (sync context): the next rebuild call picks it up
                pass

    async def _debounced(self) -> None:
        while self._dirty_since is not None:
            now = time.monotonic()
            quiet = now - self._last_write
            waited = now - self._dirty_since
            if quiet < self.debounce and waited < self.max_delay:
                await asyncio.sleep(min(self.debounce - quiet, self.max_delay - waited) + 0.01)
                continue
            self._dirty_since = None
            try:
                await self.rebuild()
            except Exception:  # noqa: BLE001 - logged; the next write triggers another attempt
                log.exception("rebuilding the Aurelius search documents failed")

    async def close(self) -> None:
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass

    async def flush(self) -> None:
        """Wait until pending changes are reflected in the search documents (tests, admin)."""
        while self._task is not None and not self._task.done():
            await self._task
        if self._dirty_since is not None:
            self._dirty_since = None
            await self.rebuild()

    async def settle(self) -> None:
        """Rebuild now if changes are pending (skips the debounce; used after API writes)."""
        if self._dirty_since is None:
            return
        self._dirty_since = None
        await self.rebuild()

    # ------------------------------------------------------------------ rebuild
    async def load_graph(self) -> Dict[str, dict]:
        store, reg = self.store, self.s.typedefs.registry
        docs: Dict[str, dict] = {}
        async for _id, src in store.scan(store.entities, {"terms": {"typeName": READ_TYPES}}):
            docs[src["guid"]] = src
        rels_by_end: Dict[str, List[dict]] = defaultdict(list)
        others: Dict[str, dict] = dict(docs)
        missing = set()
        async for _id, r in store.scan(store.relationships, {"bool": {"should": [
                {"terms": {"end1Type": READ_TYPES}}, {"terms": {"end2Type": READ_TYPES}}],
                "minimum_should_match": 1}}):
            for end in ("end1Guid", "end2Guid"):
                if r.get(end) in docs:
                    rels_by_end[r[end]].append(r)
                other = r.get("end2Guid" if end == "end1Guid" else "end1Guid")
                if other and other not in others:
                    missing.add(other)
        if missing:
            others.update(await store.mget(store.entities, list(missing)))
        return {g: entity_to_api(reg, d, rels_by_end.get(g, []), others) for g, d in docs.items()}

    async def quality_documents(self) -> List[dict]:
        out = []
        async for _id, src in self.store.scan(self.index(DATA_QUALITY), {"match_all": {}}, sort_field="id"):
            out.append(src)
        return out

    async def rebuild(self) -> dict:
        async with self._lock:
            t0 = time.time()
            entities = await self.load_graph()
            quality = data_quality.refresh(await self.quality_documents(), entities)
            new = build_documents(entities, quality)
            data_quality.fill_domain_names(quality, new)
            gov = build_gov_documents(entities, self.gov_rules)
            actions: List[dict] = []
            for engine, docs in ((SEARCH_DOCUMENTS, new), (DATA_QUALITY, {str(d["id"]): d for d in quality}),
                                 (GOV_QUALITY, gov)):
                actions += await self._changes(engine, docs)
            self.enabled_listener = False
            try:
                if actions:
                    await self.store.bulk(actions, refresh="true")
            finally:
                self.enabled_listener = True
            self.last_rebuild = {"documents": len(new), "govQuality": len(gov), "dataQuality": len(quality),
                                 "written": sum(1 for a in actions if a["op"] == "index"),
                                 "deleted": sum(1 for a in actions if a["op"] == "delete"),
                                 "seconds": round(time.time() - t0, 3), "time": int(time.time() * 1000)}
            log.info("Aurelius documents: %(documents)d search, %(govQuality)d governance quality, %(dataQuality)d "
                     "data quality; %(written)d written, %(deleted)d deleted in %(seconds).2fs", self.last_rebuild)
            return self.last_rebuild

    async def _changes(self, engine: str, docs: Dict[str, dict]) -> List[dict]:
        idx = self.index(engine)
        old: Dict[str, dict] = {}
        async for _id, src in self.store.scan(idx, {"match_all": {}}, sort_field="id"):
            old[_id] = src
        actions = [{"op": "index", "index": idx, "id": g, "doc": d} for g, d in docs.items() if old.get(g) != d]
        actions += [{"op": "delete", "index": idx, "id": g} for g in old if g not in docs]
        return actions

    # ------------------------------------------------------------------ data quality results
    async def post_quality_results(self, results: List[dict]) -> dict:
        """Store data quality scores (see :mod:`.data_quality`); the search documents follow (debounced)."""
        entities = await self.load_graph()
        refs = [str(r.get("quality") or r.get("qualityGuid") or r.get("qualityQualifiedName") or "")
                for r in results]
        found, unknown = data_quality.resolve([r for r in refs if r], entities)
        actions, idx = [], self.index(DATA_QUALITY)
        for ref, r in zip(refs, results):
            rule = found.get(ref)
            if rule is None:
                continue
            doc = data_quality.new_document(rule, entities, r["dqscore"], r.get("businessRuleId"),
                                            r.get("dataDomainName"))
            actions.append({"op": "index", "index": idx, "id": str(doc["id"]), "doc": doc})
        if actions:
            await self.store.bulk(actions, refresh="true")
            self.mark_stale()
        return {"written": len(actions), "unknown": unknown + [r for r in refs if not r]}

    async def delete_quality_results(self, refs: Optional[List[str]]) -> dict:
        """Remove the results of the given rules (guids or qualified names), or all results for ``None``."""
        idx = self.index(DATA_QUALITY)
        ids = []
        async for _id, src in self.store.scan(idx, {"match_all": {}}, sort_field="id"):
            if refs is None or {_id, src.get("qualityguid"), src.get("qualityqualifiedname")} & set(refs):
                ids.append(_id)
        if ids:
            await self.store.bulk([{"op": "delete", "index": idx, "id": i} for i in ids], refresh="true")
            self.mark_stale()
        return {"deleted": len(ids)}
