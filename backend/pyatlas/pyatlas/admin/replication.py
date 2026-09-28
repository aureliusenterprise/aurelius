"""Replication bookkeeping for export/import (Atlas ``AuditsWriter`` + ``AtlasServerService``).

With the ``replicatedTo`` export option (``replicatedFrom`` on import) Atlas

* creates/updates an ``AtlasServer`` entity for the other server (``name`` = part after ``$`` of the
  full name ``<dc>$<server>``) and records the change marker of the transfer in its ``additionalInfo``
  (``REPL_DETAILS``: ``{"<replication key guid>": <changeMarker>}``; the key is the hive_db of an exported
  hive_table / hive_column, otherwise the first exported entity),
* adds that server as a soft reference to the ``replicatedTo`` / ``replicatedFrom`` attribute of every
  exported / imported entity (unless ``skipUpdateReplicationAttr=true``),
* always makes sure an ``AtlasServer`` entity for the current server exists.
"""
from __future__ import annotations

import json
import logging
from typing import Iterable, List, Optional

from ..errors import AtlasBaseException
from ..repository.converter import build_index_fields, strip_internal

log = logging.getLogger(__name__)
SERVER_TYPE = "AtlasServer"
REPL_DETAILS = "REPL_DETAILS"


def server_name_from_full_name(full_name: Optional[str]) -> str:
    if not full_name or "$" not in full_name:
        return full_name or ""
    parts = [p for p in full_name.split("$") if p]
    if not parts:
        return ""
    return parts[1] if len(parts) >= 2 else parts[0]


class AtlasServerService:
    def __init__(self, services):
        self.s = services

    @property
    def available(self) -> bool:
        return SERVER_TYPE in self.s.typedefs.registry.entities

    async def get_or_create(self, name: str, full_name: str, user: str = "admin") -> Optional[dict]:
        if not self.available or not full_name:
            return None
        ent = self.s.entities
        guid = await ent.find_guid_by_unique_attributes(SERVER_TYPE, {"fullName": full_name})
        if guid is None:
            res = await ent.create_or_update({"entity": {"typeName": SERVER_TYPE, "attributes": {
                "name": name or full_name, "displayName": name or full_name, "fullName": full_name}}}, user)
            guid = (res.get("mutatedEntities") or {}).get("CREATE", [{}])[0].get("guid")
            if guid is None:
                guid = await ent.find_guid_by_unique_attributes(SERVER_TYPE, {"fullName": full_name})
        return await self.s.store.get(self.s.store.entities, guid) if guid else None

    async def set_replication_marker(self, server: dict, key_guid: str, marker: int, user: str) -> None:
        info = dict((server.get("attributes") or {}).get("additionalInfo") or {})
        try:
            details = json.loads(info.get(REPL_DETAILS) or "{}")
        except ValueError:
            details = {}
        if marker:
            details[key_guid] = marker
        else:
            details.pop(key_guid, None)
        info[REPL_DETAILS] = json.dumps(details)
        await self.s.entities.create_or_update({"entity": {"typeName": SERVER_TYPE, "guid": server["guid"],
                                                           "attributes": {"additionalInfo": info}}}, user,
                                               is_partial=True)

    async def replication_key(self, guid: str) -> str:
        """``AuditsWriter.ReplKeyGuidFinder``: hive_table / hive_column are keyed by their hive_db."""
        doc = await self.s.store.get(self.s.store.entities, guid)
        if doc is None or doc.get("typeName") not in ("hive_table", "hive_column"):
            return guid
        qn = str((doc.get("attributes") or {}).get("qualifiedName") or "")
        db_qn = f"{qn.split('.', 1)[0]}@{qn.rsplit('@', 1)[1] if '@' in qn else ''}"
        try:
            g = await self.s.entities.find_guid_by_unique_attributes("hive_db", {"qualifiedName": db_qn})
        except AtlasBaseException:
            g = None
        return g or guid

    async def add_server_to_entities(self, server: dict, guids: Iterable[str], attr: str) -> None:
        """Adds ``AtlasServer:<guid>`` to the soft-reference attribute without an entity update / audit (like Atlas)."""
        store, reg = self.s.store, self.s.typedefs.registry
        ref = {"guid": server["guid"], "typeName": SERVER_TYPE}
        guids = list(dict.fromkeys(guids))
        for i in range(0, len(guids), 500):
            docs = await store.mget(store.entities, guids[i:i + 500], with_version=True)
            actions = []
            for g, d in docs.items():
                et = reg.entities.get(d.get("typeName"))
                if et is None or attr not in et.attributes:
                    continue
                cur = list((d.get("attributes") or {}).get(attr) or [])
                if any(isinstance(x, dict) and x.get("guid") == ref["guid"] for x in cur):
                    continue
                seq, term = d.get("_seq_no"), d.get("_primary_term")
                d = strip_internal(d)
                d.setdefault("attributes", {})[attr] = cur + [dict(ref)]
                build_index_fields(reg, d)
                a = {"op": "index", "index": store.entities, "id": g, "doc": d}
                if seq is not None:
                    a["if_seq_no"], a["if_primary_term"] = seq, term
                actions.append(a)
            if actions:
                await store.bulk(actions)

    async def record(self, full_name: Optional[str], guids: List[str], attr: str, marker: int,
                     skip_update_attr: bool, user: str) -> None:
        """Called after a successful export (attr=replicatedTo) or import (attr=replicatedFrom)."""
        if not self.available:
            return
        await self.get_or_create(self.s.settings.server_name, self.s.settings.server_name, user)
        if not full_name or skip_update_attr or not guids:
            return
        server = await self.get_or_create(server_name_from_full_name(full_name), full_name, user)
        if server is None:
            return
        key = await self.replication_key(guids[0])
        await self.set_replication_marker(server, key, marker, user)
        await self.add_server_to_entities(server, guids, attr)
