"""Lineage (Atlas ``LineageREST`` / ``EntityLineageService``).

Lineage is derived from the ``Process.inputs`` / ``Process.outputs`` relationships
(relationship labels ``__Process.inputs`` and ``__Process.outputs``; end1 is the
process, end2 the data set)::

    DataSet --inputs--> Process --outputs--> DataSet

The traversal mirrors Atlas: from a data set, a producing (INPUT) or consuming
(OUTPUT) process is only included when it connects to at least one further data set;
``depth`` counts process hops (0 = unlimited).  The POST variant implements
on-demand lineage with per-entity ``inputRelationsLimit`` / ``outputRelationsLimit``.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import entity_header
from ..store.es import EsStore

INPUTS = "__Process.inputs"     # end1 = Process, end2 = DataSet
OUTPUTS = "__Process.outputs"   # end1 = Process, end2 = DataSet
MAX_NODE_COUNT = 9000


class _Ctx:
    def __init__(self, on_demand: bool, constraints: Dict[str, dict], default_nodes: int):
        self.relations: Dict[Tuple[str, str], str] = {}   # (from, to) -> relationship guid
        self.guids: Set[str] = set()
        self.on_demand = on_demand
        self.constraints = constraints
        self.default_nodes = default_nodes
        self.info: Dict[str, dict] = {}
        self.edge_cache: Dict[Tuple[str, str, str], List[dict]] = {}

    def constraint(self, guid: str) -> dict:
        c = dict(self.constraints.get(guid) or {})
        c.setdefault("direction", "BOTH")
        c["direction"] = c.get("direction") or "BOTH"
        if not c.get("inputRelationsLimit"):
            c["inputRelationsLimit"] = self.default_nodes
        if not c.get("outputRelationsLimit"):
            c["outputRelationsLimit"] = self.default_nodes
        if not c.get("depth"):
            c["depth"] = 3
        return c

    def node_info(self, guid: str) -> dict:
        if guid not in self.info:
            self.info[guid] = {"hasMoreInputs": False, "hasMoreOutputs": False, "inputRelationsCount": 0,
                               "outputRelationsCount": 0, "_inLimit": False, "_outLimit": False,
                               "onDemandConstraints": self.constraint(guid)}
        return self.info[guid]


def _edge_key(r: dict) -> Tuple[str, str]:
    # relation direction as Atlas reports it
    if r["label"] == INPUTS:
        return r["end2Guid"], r["end1Guid"]      # data set -> process
    return r["end1Guid"], r["end2Guid"]          # process -> data set


class LineageService:
    def __init__(self, store: EsStore, typedefs, entity_store, settings):
        self.store = store
        self.typedefs = typedefs
        self.entities = entity_store
        self.settings = settings

    async def _edges(self, ctx: _Ctx, label: str, end_field: str, guid: str) -> List[dict]:
        key = (label, end_field, guid)
        if key not in ctx.edge_cache:
            q = {"bool": {"filter": [
                {"term": {"label": label}}, {"term": {end_field: guid}},
                {"bool": {"should": [{"term": {"status": "ACTIVE"}}, {"term": {"deletedByEntity": True}}],
                          "minimum_should_match": 1}}]}}
            ctx.edge_cache[key] = [r async for _, r in self.store.scan(self.store.relationships, q)]
        return ctx.edge_cache[key]

    def _add(self, ctx: _Ctx, r: dict) -> None:
        key = _edge_key(r)
        if key in ctx.relations or len(ctx.relations) > MAX_NODE_COUNT:
            return
        ctx.relations[key] = r["guid"]
        ctx.guids.update(key)

    def _limit_reached(self, ctx: _Ctx, r: dict, is_input: bool) -> bool:
        """Atlas incrementAndCheckIfRelationsLimitReached."""
        if not ctx.on_demand:
            return False
        if _edge_key(r) in ctx.relations:
            return False
        # "in" vertex = the data set side for input edges, "out" vertex = the other side
        if r["label"] == INPUTS:
            in_v, out_v = (r["end1Guid"], r["end2Guid"]) if is_input else (r["end2Guid"], r["end1Guid"])
        else:
            in_v, out_v = (r["end1Guid"], r["end2Guid"]) if is_input else (r["end2Guid"], r["end1Guid"])
        reached = False
        ii, oi = ctx.node_info(in_v), ctx.node_info(out_v)
        if ii["_inLimit"]:
            ii["hasMoreInputs"] = True
            reached = True
        else:
            self._inc(ii, "input")
        if oi["_outLimit"]:
            oi["hasMoreOutputs"] = True
            reached = True
        else:
            self._inc(oi, "output")
        return reached

    @staticmethod
    def _inc(info: dict, kind: str) -> None:
        more, flag, cnt = ("hasMoreInputs", "_inLimit", "inputRelationsCount") if kind == "input" else \
            ("hasMoreOutputs", "_outLimit", "outputRelationsCount")
        if info[more]:
            return
        if info[flag]:
            info[more] = True
            return
        info[cnt] += 1
        limit = info["onDemandConstraints"]["inputRelationsLimit" if kind == "input" else "outputRelationsLimit"]
        if info[cnt] == limit:
            info[flag] = True

    async def _traverse(self, ctx: _Ctx, ds: str, is_input: bool, depth: int, visited: Set[str]) -> None:
        if depth == 0:
            return
        visited.add(ds)
        incoming = await self._edges(ctx, OUTPUTS if is_input else INPUTS, "end2Guid", ds)
        for e in incoming:
            if self._limit_reached(ctx, e, not is_input):
                break
            proc = e["end1Guid"]
            outgoing = await self._edges(ctx, INPUTS if is_input else OUTPUTS, "end1Guid", proc)
            for o in outgoing:
                if self._limit_reached(ctx, o, is_input):
                    break
                if not ctx.on_demand:
                    self._add(ctx, e)
                    self._add(ctx, o)
                else:
                    self._add(ctx, e)
                    self._add(ctx, o)
                nxt = o["end2Guid"]
                if nxt not in visited:
                    await self._traverse(ctx, nxt, is_input, depth - 1, visited)

    async def _validate(self, guid: str):
        reg = self.typedefs.registry
        doc = await self.store.get(self.store.entities, guid)
        if doc is None:
            raise AtlasBaseException(AtlasErrorCode.INSTANCE_GUID_NOT_FOUND, guid)
        self.entities._verify("entity-read", doc, f"read entity lineage: guid={guid}")
        et = reg.entities.get(doc["typeName"])
        is_process = bool(et and et.isa("Process"))
        is_dataset = bool(et and et.isa("DataSet"))
        if not (is_process or is_dataset):
            raise AtlasBaseException(AtlasErrorCode.INVALID_LINEAGE_ENTITY_TYPE, guid, doc["typeName"])
        return doc, is_dataset

    async def _run(self, ctx: _Ctx, guid: str, is_dataset: bool, direction: str, depth: int) -> None:
        if is_dataset:
            if ctx.on_demand:
                ctx.node_info(guid)
            if direction in ("INPUT", "BOTH"):
                await self._traverse(ctx, guid, True, depth, set())
            if direction in ("OUTPUT", "BOTH"):
                await self._traverse(ctx, guid, False, depth, set())
            return
        for is_input, label in ((True, INPUTS), (False, OUTPUTS)):
            if direction not in (("INPUT", "BOTH") if is_input else ("OUTPUT", "BOTH")):
                continue
            for e in await self._edges(ctx, label, "end1Guid", guid):
                if self._limit_reached(ctx, e, is_input):
                    break
                self._add(ctx, e)
                ds = e["end2Guid"]
                if ctx.on_demand:
                    ctx.node_info(ds)
                await self._traverse(ctx, ds, is_input, depth - 1 if depth > 0 else depth, set())

    async def _result(self, ctx: _Ctx, guid: str, direction: str, depth: int) -> dict:
        reg = self.typedefs.registry
        ctx.guids.add(guid)
        docs = await self.store.mget(self.store.entities, ctx.guids)
        headers = {g: entity_header(reg, d) for g, d in docs.items()}
        authz = self.entities.authz
        if authz is not None and authz.enabled:
            for h in headers.values():
                authz.scrub_if_denied(h)
        return {
            "baseEntityGuid": guid,
            "lineageDirection": direction,
            "lineageDepth": depth,
            "guidEntityMap": headers,
            "relations": [{"fromEntityId": f, "toEntityId": t, "relationshipId": rid}
                          for (f, t), rid in ctx.relations.items()],
            "relationsOnDemand": {},
            "lineageOnDemandPayload": {},
        }

    async def lineage(self, guid: str, direction: str = "BOTH", depth: int = 3, hide_process: bool = False) -> dict:
        _, is_dataset = await self._validate(guid)
        direction = (direction or "BOTH").upper()
        if direction not in ("INPUT", "OUTPUT", "BOTH"):
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"invalid lineage direction {direction}")
        eff_depth = -1 if not depth or depth <= 0 else min(depth, self.settings.lineage_max_depth)
        ctx = _Ctx(False, {}, 3)
        await self._run(ctx, guid, is_dataset, direction, eff_depth)
        res = await self._result(ctx, guid, direction, depth)
        if hide_process:
            res["relations"], res["guidEntityMap"] = _hide_processes(res["relations"], res["guidEntityMap"],
                                                                    self.typedefs.registry, guid)
        return res

    async def lineage_on_demand(self, guid: str, constraints: Optional[Dict[str, dict]], default_nodes: int = 3) -> dict:
        _, is_dataset = await self._validate(guid)
        constraints = dict(constraints or {})
        ctx = _Ctx(True, constraints, default_nodes)
        c = ctx.constraint(guid)
        constraints.setdefault(guid, c)
        direction = str(c["direction"]).upper()
        depth = int(c["depth"])
        await self._run(ctx, guid, is_dataset, direction, -1 if depth == 0 else depth)
        res = await self._result(ctx, guid, direction, depth)
        res["relationsOnDemand"] = {
            g: {k: v for k, v in i.items() if not k.startswith("_")}
            for g, i in ctx.info.items() if i["hasMoreInputs"] or i["hasMoreOutputs"]}
        res["lineageOnDemandPayload"] = {g: ctx.constraint(g) for g in constraints}
        return res


def _hide_processes(rels, guid_map, reg, base):
    """Collapse DataSet->Process->DataSet into DataSet->DataSet edges."""
    def is_proc(g):
        h = guid_map.get(g)
        t = reg.entities.get(h["typeName"]) if h else None
        return bool(t and t.isa("Process")) and g != base
    outgoing: Dict[str, List[Tuple[str, str]]] = {}
    for r in rels:
        outgoing.setdefault(r["fromEntityId"], []).append((r["toEntityId"], r["relationshipId"]))
    out = []
    seen = set()
    for r in rels:
        f, t = r["fromEntityId"], r["toEntityId"]
        if is_proc(f):
            continue
        if is_proc(t):
            for nxt, rid in outgoing.get(t, []):
                if (f, nxt) not in seen:
                    seen.add((f, nxt))
                    out.append({"fromEntityId": f, "toEntityId": nxt, "relationshipId": rid})
        elif (f, t) not in seen:
            seen.add((f, t))
            out.append(r)
    keep = {x for r in out for x in (r["fromEntityId"], r["toEntityId"])} | {base}
    return out, {g: h for g, h in guid_map.items() if g in keep}
