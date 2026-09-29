"""Entity audit repository (Atlas ``EntityAuditEventV2``)."""
from __future__ import annotations

import itertools
import json
import time
from typing import Any, Dict, List, Optional

from ..store.es import EsStore

_seq = itertools.count()


def audit_event(entity_id: str, action: str, user: str, details: str, ts: Optional[int] = None) -> dict:
    ts = ts or int(time.time() * 1000)
    seq = next(_seq)
    return {
        "entityId": entity_id,
        "timestamp": ts,
        "user": user,
        "action": action,
        "details": details,
        "eventKey": f"{entity_id}:{ts}:{seq}",
        "seq": seq,
    }


def details(prefix: str, payload: Any) -> str:
    return f"{prefix}: {json.dumps(payload, default=str)}"


class AuditRepository:
    def __init__(self, store: EsStore):
        self.store = store

    async def write(self, events: List[dict]) -> None:
        if not events:
            return
        await self._add_entity_names(events)
        await self.store.bulk([{"op": "index", "index": self.store.audit, "id": e["eventKey"], "doc": e} for e in events],
                              )

    async def _add_entity_names(self, events: List[dict]) -> None:
        """Type and display name of the entity with every event, so reports can group changes by type or name
        (the Atlas API output of audits is unchanged).  Purged entities are gone: their events keep neither."""
        missing = sorted({e["entityId"] for e in events if "typeName" not in e and e.get("entityId")})
        if not missing:
            return
        try:
            docs = await self.store.mget(self.store.entities, missing, source_includes=["typeName", "displayText"])
        except Exception:  # noqa: BLE001 - never fail a mutation for report fields
            return
        for e in events:
            d = docs.get(e.get("entityId"))
            if d is not None and "typeName" not in e:
                e["typeName"] = d.get("typeName")
                e["entityName"] = d.get("displayText")

    async def list_events(self, guid: str, start_key: Optional[str] = None, count: int = 100,
                          action: Optional[str] = None, sort_by: str = "timestamp", sort_order: str = "desc",
                          offset: int = 0) -> List[dict]:
        must: List[Dict[str, Any]] = [{"term": {"entityId": guid}}]
        if action:
            must.append({"term": {"action": action}})
        order = "asc" if str(sort_order).lower().startswith("asc") else "desc"
        sort_field = {"timestamp": "timestamp", "user": "user", "action": "action"}.get(sort_by or "timestamp", "timestamp")
        if start_key:
            start = await self.store.get(self.store.audit, start_key)
            if start:
                cmp = "lte" if order == "desc" else "gte"
                must.append({"range": {"timestamp": {cmp: start["timestamp"]}}})
        r = await self.store.search(self.store.audit, {"bool": {"filter": must}}, size=max(1, min(count, 10000)),
                                    from_=max(0, offset), sort=[{sort_field: order}, {"seq": order}])
        out = []
        for h in r["hits"]["hits"]:
            e = h["_source"]
            out.append({"entityId": e["entityId"], "timestamp": e["timestamp"], "user": e.get("user"),
                        "action": e["action"], "details": e.get("details"), "eventKey": e["eventKey"],
                        "type": "ENTITY_AUDIT_V2"})
        return out
