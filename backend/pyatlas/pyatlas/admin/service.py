"""Admin services: server audits, export/import audits, metrics history, tasks, async imports,
check-state, index recovery, active searches and request timing metrics."""
from __future__ import annotations

import asyncio
import copy
import json
import logging
import math
import sys
import threading
import time
import traceback
import uuid
from typing import Any, Dict, List, Optional

from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import build_index_fields, entity_header, strip_internal, unique_key
from ..store.es import EsStore

log = logging.getLogger(__name__)


def now_ms() -> int:
    return int(time.time() * 1000)


class AdminAuditService:
    """AtlasAuditEntry (``POST /admin/audits``) and ExportImportAuditEntry (``GET /admin/expimp/audit``)."""
    KIND = "adminaudit"
    EXPIMP = "expimpaudit"

    def __init__(self, store: EsStore):
        self.store = store

    async def add(self, operation: str, user: str, params: str, result: str, count: int, start: int, end: int,
                  client_id: str = "", run_id: Optional[str] = None, row_kind: Optional[str] = None) -> dict:
        e = {"guid": str(uuid.uuid4()), "userName": user, "operation": operation, "params": params,
             "startTime": start, "endTime": end, "clientId": client_id, "result": result, "resultCount": count}
        if run_id:
            e["runId"] = run_id
        if row_kind:
            e["auditRowKind"] = row_kind
        await self.store.put(self.store.meta, f"{self.KIND}:{e['guid']}",
                             {"kind": self.KIND, "name": operation, "ownerName": user, "guid": e["guid"],
                              "updateTime": start, "value": e})
        return e

    async def _all(self, kind: str) -> List[dict]:
        q = {"term": {"kind": kind}}
        return [d["value"] async for _, d in self.store.scan(self.store.meta, q, sort_field="guid", limit=100000)]

    async def get(self, guid: str) -> Optional[dict]:
        d = await self.store.get(self.store.meta, f"{self.KIND}:{guid}")
        return d["value"] if d else None

    async def search(self, p: Optional[dict]) -> List[dict]:
        p = p or {}
        entries = await self._all(self.KIND)
        run_filter = _mentions(p.get("auditFilters"), "runId")
        if not run_filter:
            entries = [e for e in entries if e.get("auditRowKind") != "BATCH"]
        entries = [e for e in entries if _match(e, p.get("auditFilters"))]
        key = p.get("sortBy") or "startTime"
        desc = str(p.get("sortOrder") or "DESCENDING").upper().startswith("DESC")
        entries.sort(key=lambda e: (e.get(key) is None, e.get(key) if e.get(key) is not None else 0), reverse=desc)
        off = int(p.get("offset") or 0)
        lim = int(p.get("limit") or 0) or len(entries)
        return entries[off:off + lim]

    async def add_expimp(self, user: str, operation: str, params: str, summary: str, start: int, end: int,
                         source: str, target: str) -> None:
        guid = str(uuid.uuid4())
        e = {"guid": guid, "userName": user, "operation": operation, "operationParams": params, "startTime": start,
             "endTime": end, "resultSummary": summary, "sourceServerName": source, "targetServerName": target}
        await self.store.put(self.store.meta, f"{self.EXPIMP}:{guid}",
                             {"kind": self.EXPIMP, "name": operation, "ownerName": user, "guid": guid,
                              "updateTime": start, "value": e})

    async def expimp(self, user: Optional[str], operation: Optional[str], server: Optional[str], start: Optional[str],
                     end: Optional[str], limit: int, offset: int) -> List[dict]:
        out = []
        for e in await self._all(self.EXPIMP):
            if user and e.get("userName") != user:
                continue
            if operation and e.get("operation") != operation:
                continue
            if server and server not in (e.get("sourceServerName"), e.get("targetServerName")):
                continue
            if start and e["startTime"] < int(start):
                continue
            if end and e["endTime"] > int(end):
                continue
            out.append(e)
        out.sort(key=lambda e: e["startTime"], reverse=True)
        return out[offset:offset + (limit or len(out))]


def _mentions(criteria: Optional[dict], attr: str) -> bool:
    if not criteria:
        return False
    if criteria.get("attributeName") == attr:
        return True
    return any(_mentions(c, attr) for c in criteria.get("criterion") or [])


def _match(entry: dict, criteria: Optional[dict]) -> bool:
    if not criteria:
        return True
    if criteria.get("criterion"):
        res = [_match(entry, c) for c in criteria["criterion"]]
        return any(res) if str(criteria.get("condition") or "AND").upper() == "OR" else all(res)
    attr = criteria.get("attributeName")
    if not attr:
        return True
    op = str(criteria.get("operator") or "eq").lower()
    want = criteria.get("attributeValue")
    have = entry.get(attr)
    if op in ("isnull", "is_null"):
        return have in (None, "")
    if op in ("notnull", "not_null", "notempty", "not_empty"):
        return have not in (None, "")
    if have is None:
        return op in ("!=", "neq", "not_contains")
    if isinstance(have, (int, float)) and not isinstance(have, bool):
        try:
            w = float(want)
        except (TypeError, ValueError):
            from ..discovery.filters import time_range
            if op in ("timerange", "time_range"):
                a, b = time_range(want)
                return a <= have <= b
            return False
        return {"=": have == w, "eq": have == w, "!=": have != w, "neq": have != w, "<": have < w, "lt": have < w,
                ">": have > w, "gt": have > w, "<=": have <= w, "lte": have <= w, ">=": have >= w,
                "gte": have >= w}.get(op, False)
    hs, ws = str(have).lower(), str(want).lower()
    return {"=": hs == ws, "eq": hs == ws, "!=": hs != ws, "neq": hs != ws, "contains": ws in hs,
            "not_contains": ws not in hs, "startswith": hs.startswith(ws), "begins_with": hs.startswith(ws),
            "endswith": hs.endswith(ws), "like": ws.replace("*", "") in hs,
            "in": hs in [x.strip().lower() for x in str(want).split(",")]}.get(op, False)


class MetricsStatsService:
    KIND = "metricsstat"

    def __init__(self, services):
        self.s = services
        self._task: Optional[asyncio.Task] = None

    async def save_now(self) -> dict:
        metrics = await self.s.metrics()
        ct = metrics["data"]["general"]["collectionTime"]
        ttl = int(self.s.settings.metrics_ttl_hours) * 3600 * 1000
        stat = {"guid": str(uuid.uuid4()), "metricsId": f"atlas_metrics_{ct}@{self.s.settings.server_name}",
                "collectionTime": ct, "timeToLiveMillis": ttl, "metrics": metrics}
        await self.s.store.put(self.s.store.meta, f"{self.KIND}:{ct}",
                               {"kind": self.KIND, "name": stat["metricsId"], "guid": stat["guid"], "updateTime": ct,
                                "value": stat})
        await self.purge()
        return stat

    async def purge(self) -> None:
        now = now_ms()
        for st in await self.all(False):
            if st["collectionTime"] + st.get("timeToLiveMillis", 0) < now:
                await self.s.store.delete(self.s.store.meta, f"{self.KIND}:{st['collectionTime']}")

    async def all(self, min_info: bool = True) -> List[dict]:
        out = [d["value"] async for _, d in self.s.store.scan(self.s.store.meta, {"term": {"kind": self.KIND}},
                                                                   sort_field="guid")]
        out.sort(key=lambda x: -x["collectionTime"])
        if min_info:
            out = [{k: v for k, v in x.items() if k != "metrics"} for x in out]
        return out

    async def by_time(self, ct: str) -> dict:
        d = await self.s.store.get(self.s.store.meta, f"{self.KIND}:{ct}")
        if d is None:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"no metrics collected at {ct}")
        return d["value"]

    async def range(self, start: int, end: int, type_names: List[str]) -> List[dict]:
        if start >= end:
            raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS,
                                     f"startTime: '{start}', should be less than, endTime: '{end}'")
        out = []
        for st in await self.all(False):
            if start <= st["collectionTime"] <= end:
                ent = st["metrics"]["data"]["entity"]
                type_data = {t: {k: int(ent.get("entity" + k, {}).get(t, 0)) for k in ("Active", "Deleted", "Shell")}
                             for t in type_names} if type_names else None
                x = {k: v for k, v in st.items() if k != "metrics"}
                if type_data is not None:
                    x["typeData"] = type_data
                out.append(x)
        return out

    async def charts(self, start: int, end: int, type_names: List[str]) -> Dict[str, List[dict]]:
        stats = list(reversed(await self.range(start, end, type_names)))
        out: Dict[str, List[dict]] = {}
        for t in type_names:
            series = {k: [] for k in ("Active", "Deleted", "Shell")}
            for st in stats:
                for k in series:
                    series[k].append([st["collectionTime"], (st.get("typeData") or {}).get(t, {}).get(k, 0)])
            out[t] = [{"key": k, "values": v} for k, v in series.items()] if stats else []
        return out

    def start_scheduler(self) -> None:
        interval = self.s.settings.metrics_persist_interval_secs
        if interval <= 0 or self._task is not None:
            return

        async def loop():
            while True:
                await asyncio.sleep(interval)
                try:
                    await self.save_now()
                except Exception:  # pragma: no cover
                    log.exception("could not persist metrics")
        self._task = asyncio.get_running_loop().create_task(loop())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None


class AsyncImportService:
    KIND = "asyncimport"

    def __init__(self, services):
        self.s = services
        self.aborts: Dict[str, asyncio.Event] = {}
        self._bg: set = set()

    async def _save(self, req: dict) -> None:
        await self.s.store.put(self.s.store.meta, f"{self.KIND}:{req['importId']}",
                               {"kind": self.KIND, "name": req["status"], "ownerName": req.get("_user"),
                                "guid": req["importId"], "updateTime": now_ms(), "value": req}, refresh="true")

    async def submit(self, data: bytes, request: dict, user: str, client_ip: str) -> dict:
        import_id = uuid.uuid4().hex
        req = {"importId": import_id, "status": "STAGING", "receivedTime": now_ms(), "stagedTime": 0,
               "processingStartTime": 0, "completedTime": 0,
               "importDetails": {"publishedEntityCount": 0, "totalEntitiesCount": 0, "importedEntitiesCount": 0,
                                 "failedEntitiesCount": 0, "failedEntities": [], "importProgress": 0.0, "failures": {}},
               "importTrackingInfo": {"requestId": import_id, "startEntityPosition": 0},
               "_user": user}
        await self._save(req)
        req["status"] = "WAITING"
        req["stagedTime"] = now_ms()
        await self._save(req)
        ev = asyncio.Event()
        self.aborts[import_id] = ev

        async def run():
            req["status"] = "PROCESSING"
            req["processingStartTime"] = now_ms()
            await self._save(req)

            async def progress(done, total, failed):
                d = req["importDetails"]
                d["totalEntitiesCount"] = total
                d["publishedEntityCount"] = done
                d["importedEntitiesCount"] = done - failed
                d["failedEntitiesCount"] = failed
                d["importProgress"] = round(100.0 * done / total, 2) if total else 100.0
            try:
                res = await self.s.impexp.import_zip(data, request, user, client_ip, progress=progress, abort=ev)
                req["importResult"] = res
                d = req["importDetails"]
                d["failures"] = res.get("failures") or {}
                d["failedEntities"] = list(d["failures"])
                if ev.is_set():
                    req["status"] = "ABORTED"
                else:
                    req["status"] = {"SUCCESS": "SUCCESSFUL", "PARTIAL_SUCCESS": "PARTIAL_SUCCESS"}.get(
                        res["operationStatus"], "FAILED")
            except Exception as e:  # pragma: no cover
                log.exception("async import %s failed", import_id)
                req["status"] = "FAILED"
                req["importDetails"]["failures"] = {"import": str(e)}
            req["completedTime"] = now_ms()
            await self._save(req)
            self.aborts.pop(import_id, None)
        t = asyncio.get_running_loop().create_task(run())
        self._bg.add(t)
        t.add_done_callback(self._bg.discard)
        return _public(req)

    async def wait_all(self) -> None:
        if self._bg:
            await asyncio.gather(*list(self._bg), return_exceptions=True)

    async def get(self, import_id: str) -> dict:
        d = await self.s.store.get(self.s.store.meta, f"{self.KIND}:{import_id}")
        if d is None:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"import {import_id} not found")
        return _public(d["value"])

    async def list(self, offset: int, limit: int) -> dict:
        items = [d["value"] async for _, d in self.s.store.scan(self.s.store.meta, {"term": {"kind": self.KIND}},
                                                                     sort_field="guid")]
        items.sort(key=lambda r: -r["receivedTime"])
        page = items[offset:offset + limit]
        lst = [{"importId": r["importId"], "status": r["status"],
                "importRequestReceivedTime": _iso(r["receivedTime"]), "importRequestUser": r.get("_user")} for r in page]
        return {"list": lst, "startIndex": offset, "pageSize": len(lst), "totalCount": len(items), "sortType": "NONE"}

    async def abort(self, import_id: str) -> None:
        req = await self.get(import_id)
        if req["status"] in ("SUCCESSFUL", "PARTIAL_SUCCESS", "FAILED", "ABORTED"):
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"import {import_id} is already {req['status']}")
        ev = self.aborts.get(import_id)
        if ev is not None:
            ev.set()
        else:
            d = await self.s.store.get(self.s.store.meta, f"{self.KIND}:{import_id}")
            v = d["value"]
            v["status"] = "ABORTED"
            v["completedTime"] = now_ms()
            await self._save(v)


def _public(req: dict) -> dict:
    return {k: v for k, v in req.items() if not k.startswith("_")}


def _iso(ms: int) -> str:
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ms / 1000, _dt.timezone.utc).isoformat().replace("+00:00", "Z")


class RequestMetrics:
    """Per-endpoint timing statistics for ``GET /admin/debug/metrics`` (Atlas DebugMetrics)."""

    def __init__(self):
        self.stats: Dict[str, List[float]] = {}

    def record(self, name: str, ms: float) -> None:
        s = self.stats.setdefault(name, [0, 0.0, 0.0, math.inf, 0.0])   # n, sum, sumsq, min, max
        s[0] += 1
        s[1] += ms
        s[2] += ms * ms
        s[3] = min(s[3], ms)
        s[4] = max(s[4], ms)

    def report(self) -> Dict[str, dict]:
        out = {}
        for name, (n, total, sq, mn, mx) in self.stats.items():
            avg = total / n if n else 0.0
            var = max(0.0, sq / n - avg * avg) if n else 0.0
            out[name] = {"name": name, "numops": n, "minTime": round(mn, 3), "maxTime": round(mx, 3),
                         "avgTime": round(avg, 3), "stdDevTime": round(math.sqrt(var), 3)}
        return out


class TaskStore:
    """Persistent ``AtlasTask`` records (Atlas keeps them as ``__AtlasTaskDef`` vertices) in the meta index."""
    KIND = "task"

    def __init__(self, store):
        self.store = store

    async def add(self, task: dict) -> dict:
        await self.store.put(self.store.meta, f"{self.KIND}:{task['guid']}",
                             {"kind": self.KIND, "name": task.get("type"), "ownerName": task.get("createdBy"),
                              "guid": task["guid"], "updateTime": task.get("updatedTime") or now_ms(), "value": task},
                             refresh="true")
        return task

    async def list(self, guids: Optional[List[str]] = None) -> List[dict]:
        q: dict = {"term": {"kind": self.KIND}}
        if guids:
            q = {"bool": {"filter": [q, {"terms": {"guid": list(guids)}}]}}
        out = [d["value"] async for _, d in self.store.scan(self.store.meta, q, sort_field="guid")]
        out.sort(key=lambda t: t.get("createdTime") or 0)
        return out

    async def delete(self, guids: List[str]) -> None:
        for g in guids:
            await self.store.delete(self.store.meta, f"{self.KIND}:{g}", refresh="true")


class ActiveSearches:
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}

    def register(self, user: str) -> str:
        sid = f"{user}:{uuid.uuid4().hex}"
        t = asyncio.current_task()
        if t is not None:
            self.tasks[sid] = t
        return sid

    def unregister(self, sid: str) -> None:
        self.tasks.pop(sid, None)

    def owner(self, sid: str) -> Optional[str]:
        return sid.split(":", 1)[0] if sid in self.tasks else None

    def list(self) -> List[str]:
        return sorted(self.tasks)

    def terminate(self, sid: str) -> bool:
        t = self.tasks.pop(sid, None)
        if t is None:
            return False
        t.cancel()
        return True


def thread_dump() -> str:
    lines = []
    frames = sys._current_frames()
    for th in threading.enumerate():
        lines.append(f'"{th.name}" daemon={th.daemon} id={th.ident}')
        f = frames.get(th.ident)
        if f is not None:
            lines.extend("    " + x.rstrip() for x in traceback.format_stack(f))
        lines.append("")
    try:
        for t in asyncio.all_tasks():
            lines.append(f"asyncio task {t.get_name()}: {t.get_coro()}")
    except RuntimeError:
        pass
    return "\n".join(lines)


async def check_state(services, request: dict) -> dict:
    """Validate (and optionally fix) derived data of entity documents."""
    reg = services.typedefs.registry
    store = services.store
    fix = bool(request.get("fixIssues"))
    guids = set(request.get("entityGuids") or [])
    types = set(request.get("entityTypes") or [])
    if types:
        q = {"terms": {"typeName": sorted({t for n in types if n in reg.entities for t in reg.entities[n].type_and_all_sub_types()})}}
        async for g, _ in store.scan(store.entities, q, source=["guid"], limit=1000000):
            guids.add(g)
    result = {"entitiesScanned": 0, "entitiesOk": 0, "entitiesFixed": 0, "entitiesPartiallyFixed": 0,
              "entitiesNotFixed": 0, "state": "OK", "entities": {}}
    docs = await store.mget(store.entities, guids, with_version=True)
    for g in guids:
        result["entitiesScanned"] += 1
        d = docs.get(g)
        if d is None:
            result["entities"][g] = {"guid": g, "state": "NOT_FIXED", "issues": ["entity not found"]}
            result["entitiesNotFixed"] += 1
            continue
        issues = []
        et = reg.entities.get(d["typeName"])
        if et is None:
            issues.append(f"unknown type {d['typeName']}")
        clean = strip_internal(copy.deepcopy(d))
        expect = build_index_fields(reg, copy.deepcopy(clean))
        for k in ("classificationNames", "propagatedClassificationNames", "displayText", "idx", "superTypeNames"):
            if expect.get(k) != d.get(k):
                issues.append(f"index field {k} is stale")
        missing_keys = []
        if et is not None and d.get("status") == "ACTIVE":
            for u in et.unique_attributes:
                v = (d.get("attributes") or {}).get(u)
                if v is None:
                    continue
                k = unique_key(d["typeName"], u, v)
                owner = await store.get(store.unique, k)
                if owner is None or owner.get("guid") != g:
                    issues.append(f"unique attribute {u} not registered")
                    missing_keys.append((k, u))
        state = {"guid": g, "typeName": d["typeName"], "name": d.get("displayText"), "status": d.get("status"),
                 "state": "OK"}
        if issues:
            state["issues"] = issues
            if fix:
                await store.put(store.entities, g, expect)
                for k, u in missing_keys:
                    await store.put(store.unique, k, {"guid": g, "typeName": d["typeName"], "attribute": u, "ts": now_ms()})
                state["state"] = "FIXED"
                result["entitiesFixed"] += 1
            else:
                state["state"] = "NOT_FIXED"
                result["entitiesNotFixed"] += 1
            result["entities"][g] = state
        else:
            result["entitiesOk"] += 1
    if result["entitiesNotFixed"]:
        result["state"] = "NOT_FIXED"
    elif result["entitiesFixed"]:
        result["state"] = "FIXED"
    if not result["entities"]:
        result.pop("entities")
    return result


async def reindex(services, since_ms: int) -> int:
    """Rebuild the search fields of all entities modified since ``since_ms`` (index recovery)."""
    reg = services.typedefs.registry
    store = services.store
    q = {"range": {"updateTime": {"gte": since_ms}}}
    n = 0
    batch = []
    async for g, d in store.scan(store.entities, q):
        batch.append({"op": "index", "index": store.entities, "id": g, "doc": build_index_fields(reg, d)})
        if len(batch) >= 500:
            await store.bulk(batch, refresh="false")
            n += len(batch)
            batch = []
    if batch:
        await store.bulk(batch, refresh="false")
        n += len(batch)
    await store.es.indices.refresh(index=store.entities)
    return n


async def ageout_audits(services, c: dict, user: str = "admin") -> List[dict]:
    """Atlas audit reduction: remove entity audit events by age (TTL) and/or keep only the newest N per entity."""
    store = services.store
    now = now_ms()
    tasks = []

    async def run(kind: str, ttl_days: int, keep: int, types: Optional[str], actions: Optional[str], sweep: bool) -> dict:
        must: List[dict] = []
        if actions:
            must.append({"terms": {"action": [a.strip() for a in actions.split(",") if a.strip()]}})
        guids: Optional[List[str]] = None
        if types:
            reg = services.typedefs.registry
            names = set()
            for t in (x.strip() for x in types.split(",") if x.strip()):
                if t in reg.entities:
                    names |= reg.entities[t].type_and_all_sub_types() if c.get("subTypesIncluded") else {t}
            guids = [g async for g, _ in store.scan(store.entities, {"terms": {"typeName": sorted(names) or ["-"]}},
                                                    source=["guid"], limit=1000000)]
            must.append({"terms": {"entityId": guids or ["-"]}})
        deleted = 0
        if sweep:
            deleted += await store.delete_by_query(store.audit, {"bool": {"filter": must}} if must else {"match_all": {}})
        else:
            if ttl_days and ttl_days > 0:
                q = {"bool": {"filter": must + [{"range": {"timestamp": {"lt": now - ttl_days * 86400000}}}]}}
                if not c.get("createEventsAgeoutAllowed"):
                    q["bool"]["must_not"] = [{"term": {"action": "ENTITY_CREATE"}}]
                deleted += await store.delete_by_query(store.audit, q)
            if keep and keep > 0:
                per: Dict[str, List[dict]] = {}
                async for _id, e in store.scan(store.audit, {"bool": {"filter": must}} if must else {"match_all": {}},
                                               sort_field="eventKey", limit=1000000):
                    per.setdefault(e["entityId"], []).append(e)
                drop = []
                for evs in per.values():
                    evs.sort(key=lambda e: (e["timestamp"], e.get("seq", 0)), reverse=True)
                    for e in evs[keep:]:
                        if e["action"] == "ENTITY_CREATE" and not c.get("createEventsAgeoutAllowed"):
                            continue
                        drop.append(e["eventKey"])
                await store.bulk([{"op": "delete", "index": store.audit, "id": k} for k in drop])
                deleted += len(drop)
        # Atlas queues an AUDIT_REDUCTION_ENTITY_RETRIEVAL task per aging type; here it runs right away
        task = {"type": "AUDIT_REDUCTION_ENTITY_RETRIEVAL", "guid": str(uuid.uuid4()), "createdBy": user,
                "createdTime": now, "updatedTime": now_ms(), "startTime": now, "endTime": now_ms(),
                "parameters": {"auditAgingType": kind, "ttl": ttl_days, "auditCount": keep,
                               "entityTypes": types, "actionTypes": actions,
                               "createEventsAgeoutAllowed": bool(c.get("createEventsAgeoutAllowed")),
                               "subTypesIncluded": bool(c.get("subTypesIncluded")), "deletedEvents": deleted},
                "attemptCount": 1, "status": "COMPLETE"}
        return await services.tasks.add(task)
    if c.get("defaultAgeoutEnabled", True) and not c.get("ignoreDefaultAgeoutTTL"):
        tasks.append(await run("DEFAULT", int(c.get("defaultAgeoutTTLInDays") or 0),
                               int(c.get("defaultAgeoutAuditCount") or 0), None, None, False))
    if c.get("customAgeoutTTLInDays") or c.get("customAgeoutAuditCount"):
        tasks.append(await run("CUSTOM", int(c.get("customAgeoutTTLInDays") or 0), int(c.get("customAgeoutAuditCount") or 0),
                               c.get("customAgeoutEntityTypes"), c.get("customAgeoutActionTypes"), False))
    if c.get("auditSweepoutEnabled"):
        tasks.append(await run("SWEEP", 0, 0, c.get("sweepoutEntityTypes"), c.get("sweepoutActionTypes"), True))
    return tasks
