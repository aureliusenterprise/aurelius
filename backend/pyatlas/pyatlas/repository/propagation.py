"""Classification (tag) propagation.

Atlas propagates a classification from the entity it is attached to along
relationships whose ``propagateTags`` allows it (ONE_TO_TWO, TWO_TO_ONE, BOTH),
e.g. from a table through a process to derived tables.

Instead of incrementally patching graph edges, pyatlas recomputes propagation per
*(source entity, classification type)* pair: a breadth-first walk over the
relationship index determines which entities should carry the propagated copy,
and the difference with what is stored is written back.  The entity store calls
:meth:`Propagator.recompute` for every pair that may be affected by a change.
"""
from __future__ import annotations

import copy
import logging
import time
from typing import Dict, Iterable, List, Optional, Set, Tuple

from ..store.es import EsStore
from ..typesystem.registry import TypeRegistry
from .audit import audit_event, details
from .converter import build_index_fields, classification_to_api, strip_internal

log = logging.getLogger(__name__)

Pair = Tuple[str, str]  # (source guid, classification type)


class Propagator:
    def __init__(self, store: EsStore, registry_getter, max_entities: int = 100000):
        self.store = store
        self._reg = registry_getter
        self.max_entities = max_entities

    @property
    def reg(self) -> TypeRegistry:
        return self._reg()

    async def recompute(self, pairs: Iterable[Pair], user: str) -> List[dict]:
        audits: List[dict] = []
        self._walks: Dict[Tuple[str, bool], List[Tuple[str, str, dict]]] = {}
        self._node_rels: Dict[Tuple[str, bool], List[Tuple[str, dict]]] = {}
        for src, ttype in sorted(set(pairs)):
            try:
                audits += await self._recompute_one(src, ttype, user)
            except Exception:  # pragma: no cover - never fail the user's request because of propagation
                log.exception("propagation of %s from %s failed", ttype, src)
        return audits

    async def _recompute_one(self, src: str, ttype: str, user: str) -> List[dict]:
        src_doc = await self.store.get(self.store.entities, src)
        tag = None
        if src_doc is not None:
            tag = next((c for c in src_doc.get("classifications") or [] if c["typeName"] == ttype), None)
        reachable: Set[str] = set()
        if tag is not None and tag.get("propagate", True):
            remove_on_delete = bool(tag.get("removePropagationsOnEntityDelete", False))
            if not (src_doc.get("status") == "DELETED" and remove_on_delete):
                reachable = await self._reachable(src, ttype, remove_on_delete)
        reachable.discard(src)

        current = await self._current_holders(src, ttype)
        to_touch = (reachable | current)
        if not to_touch:
            return []
        docs = await self.store.mget(self.store.entities, to_touch, with_version=True)
        now = int(time.time() * 1000)
        actions, audits = [], []
        for guid, doc in docs.items():
            props = doc.get("propagatedClassifications") or []
            existing = next((c for c in props if c["typeName"] == ttype and c.get("entityGuid") == src), None)
            if guid in reachable:
                new_c = {
                    "typeName": ttype,
                    "attributes": copy.deepcopy(tag.get("attributes") or {}),
                    "entityGuid": src,
                    "entityStatus": src_doc.get("status", "ACTIVE"),
                    "propagate": True,
                    "removePropagationsOnEntityDelete": tag.get("removePropagationsOnEntityDelete", False),
                }
                if tag.get("validityPeriods"):
                    new_c["validityPeriods"] = tag["validityPeriods"]
                if existing == new_c:
                    continue
                props = [c for c in props if not (c["typeName"] == ttype and c.get("entityGuid") == src)] + [new_c]
                action = "PROPAGATED_CLASSIFICATION_UPDATE" if existing else "PROPAGATED_CLASSIFICATION_ADD"
                audits.append(audit_event(guid, action, user, details(
                    "Updated propagated classification" if existing else "Added propagated classification",
                    classification_to_api(new_c, src, new_c["entityStatus"])), now))
            else:
                if existing is None:
                    continue
                props = [c for c in props if not (c["typeName"] == ttype and c.get("entityGuid") == src)]
                audits.append(audit_event(guid, "PROPAGATED_CLASSIFICATION_DELETE", user,
                                          details("Deleted propagated classification", {"typeName": ttype, "entityGuid": src}), now))
            doc["propagatedClassifications"] = props
            seq, term = doc.get("_seq_no"), doc.get("_primary_term")
            doc = strip_internal(doc)
            build_index_fields(self.reg, doc)
            actions.append({"op": "index", "index": self.store.entities, "id": guid, "doc": doc,
                            "if_seq_no": seq, "if_primary_term": term})
        results = await self.store.bulk(actions)
        conflicts = [r["id"] for r in results if r["status"] == 409]
        if conflicts:
            # somebody modified these entities in between; retry just those once more
            log.info("propagation conflict on %d entities, retrying", len(conflicts))
            await self._retry(conflicts, src, ttype, tag, src_doc, reachable)
        return audits

    async def _retry(self, guids, src, ttype, tag, src_doc, reachable) -> None:
        for _ in range(3):
            docs = await self.store.mget(self.store.entities, guids, with_version=True)
            actions = []
            for guid, doc in docs.items():
                props = [c for c in doc.get("propagatedClassifications") or []
                         if not (c["typeName"] == ttype and c.get("entityGuid") == src)]
                if guid in reachable and tag is not None:
                    props.append({"typeName": ttype, "attributes": copy.deepcopy(tag.get("attributes") or {}),
                                  "entityGuid": src, "entityStatus": src_doc.get("status", "ACTIVE"), "propagate": True,
                                  "removePropagationsOnEntityDelete": tag.get("removePropagationsOnEntityDelete", False)})
                doc["propagatedClassifications"] = props
                seq, term = doc.get("_seq_no"), doc.get("_primary_term")
                doc = strip_internal(doc)
                build_index_fields(self.reg, doc)
                actions.append({"op": "index", "index": self.store.entities, "id": guid, "doc": doc,
                                "if_seq_no": seq, "if_primary_term": term})
            results = await self.store.bulk(actions)
            guids = [r["id"] for r in results if r["status"] == 409]
            if not guids:
                return

    async def _current_holders(self, src: str, ttype: str) -> Set[str]:
        q = {"nested": {"path": "tags", "query": {"bool": {"filter": [
            {"term": {"tags.source": src}}, {"term": {"tags.typeName": ttype}}, {"term": {"tags.propagated": True}}]}}}}
        out = set()
        async for gid, _ in self.store.scan(self.store.entities, q, source=["guid"]):
            out.add(gid)
        return out

    async def _reachable(self, src: str, ttype: str, remove_on_delete: bool) -> Set[str]:
        """Entities reachable from ``src`` over propagating relationships not blocked for ``ttype``.

        The relationship walk (all propagating edges reachable from ``src``) is shared by all
        classification types of the same source within one :meth:`recompute` call."""
        walks = getattr(self, "_walks", None)
        key = (src, remove_on_delete)
        edges = walks.get(key) if walks is not None else None
        if edges is None:
            edges = await self._walk(src, remove_on_delete)
            if walks is not None:
                walks[key] = edges
        adj: Dict[str, List[str]] = {}
        for a, b, r in edges:
            if any(bl.get("typeName") == ttype and bl.get("entityGuid") in (src, None)
                   for bl in r.get("blockedPropagatedClassifications") or []):
                continue
            adj.setdefault(a, []).append(b)
        visited, frontier = {src}, [src]
        while frontier and len(visited) < self.max_entities:
            nxt = []
            for g in frontier:
                for h in adj.get(g, ()):
                    if h not in visited:
                        visited.add(h)
                        nxt.append(h)
            frontier = nxt
        return visited

    async def _walk(self, src: str, remove_on_delete: bool) -> List[Tuple[str, str, dict]]:
        """Directed propagation edges (from, to, relationship) of the component reachable from ``src``.

        The propagating relationships of each entity are fetched once per :meth:`recompute` call and
        shared between the walks of all sources."""
        cache: Dict[Tuple[str, bool], List[Tuple[str, dict]]] = getattr(self, "_node_rels", None)
        if cache is None:
            cache = {}
        edges: List[Tuple[str, str, dict]] = []
        seen_rel: Set[str] = set()
        visited = {src}
        frontier = {src}
        while frontier and len(visited) < self.max_entities:
            missing = [g for g in frontier if (g, remove_on_delete) not in cache]
            for chunk in _chunks(missing, 500):
                for g in chunk:
                    cache[(g, remove_on_delete)] = []
                status_filter = {"term": {"status": "ACTIVE"}} if remove_on_delete else {"bool": {"should": [
                    {"term": {"status": "ACTIVE"}}, {"term": {"deletedByEntity": True}}], "minimum_should_match": 1}}
                q = {"bool": {"filter": [status_filter, {"terms": {"propagateTags": ["ONE_TO_TWO", "TWO_TO_ONE", "BOTH"]}}],
                              "should": [{"terms": {"end1Guid": chunk}}, {"terms": {"end2Guid": chunk}}],
                              "minimum_should_match": 1}}
                chunk_set = set(chunk)
                async for rid, r in self.store.scan(self.store.relationships, q):
                    for end in {r["end1Guid"], r["end2Guid"]} & chunk_set:
                        cache[(end, remove_on_delete)].append((rid, r))
            nxt: Set[str] = set()
            for g in frontier:
                for rid, r in cache[(g, remove_on_delete)]:
                    if rid in seen_rel:
                        continue
                    seen_rel.add(rid)
                    pt = r.get("propagateTags")
                    if pt in ("ONE_TO_TWO", "BOTH"):
                        edges.append((r["end1Guid"], r["end2Guid"], r))
                        if r["end2Guid"] not in visited:
                            nxt.add(r["end2Guid"])
                    if pt in ("TWO_TO_ONE", "BOTH"):
                        edges.append((r["end2Guid"], r["end1Guid"], r))
                        if r["end1Guid"] not in visited:
                            nxt.add(r["end1Guid"])
            visited |= nxt
            frontier = nxt
        return edges


def _chunks(seq: List[str], n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def pairs_of(doc: Optional[dict]) -> Set[Pair]:
    """All (source, type) pairs present on an entity (direct and propagated)."""
    if not doc:
        return set()
    out = {(doc["guid"], c["typeName"]) for c in doc.get("classifications") or []}
    out |= {(c.get("entityGuid"), c["typeName"]) for c in doc.get("propagatedClassifications") or [] if c.get("entityGuid")}
    return out
