"""Export / import in the Apache Atlas ZIP format.

A ZIP produced by ``POST /api/atlas/admin/export`` contains (like Atlas' ``ZipSink``)::

    atlas-export-info.json    AtlasExportResult (without data)
    atlas-typesdef.json       AtlasTypesDef of all types needed by the exported entities
    atlas-export-order.json   list of entity guids in creation order
    <guid>.json               AtlasEntityWithExtInfo for each exported entity

so archives can be moved between Apache Atlas and pyatlas in both directions.
Import runs in two passes (entities, then relationships) so that references
between entities in the archive always resolve, and keeps the source guids
unless an entity with the same unique attributes already exists.
"""
from __future__ import annotations

import asyncio
import copy
import io
import json
import logging
import socket
import time
import uuid
import zipfile
from typing import Any, Dict, List, Optional, Set, Tuple

from ..authz import import_in_progress
from .replication import server_name_from_full_name
from .transforms import EntityTransformers, ImportTransforms
from ..errors import AtlasBaseException, AtlasErrorCode
from ..safety import check_zip
from ..typesystem.registry import (BUSINESS_METADATA, CATEGORY_LIST_KEYS, CLASSIFICATION, ENTITY, ENUM, RELATIONSHIP,
                                   STRUCT, base_type_name)

log = logging.getLogger(__name__)

INFO, ORDER, TYPES = "atlas-export-info.json", "atlas-export-order.json", "atlas-typesdef.json"


def _is_true(v) -> bool:
    return str(v).lower() == "true"


def now_ms() -> int:
    return int(time.time() * 1000)


class ExportImportService:
    def __init__(self, services):
        self.s = services
        self.lock = asyncio.Lock()

    @property
    def reg(self):
        return self.s.typedefs.registry

    # ================================================================== export
    async def _start_guids(self, item: dict, options: dict) -> List[str]:
        ent = self.s.entities
        if item.get("guid"):
            return [item["guid"]]
        type_name = item.get("typeName")
        uattrs = item.get("uniqueAttributes") or {}
        match = str(options.get("matchType") or "").lower()
        if match in ("", "equals") and uattrs:
            g = await ent.find_guid_by_unique_attributes(type_name, uattrs)
            return [g] if g else []
        if type_name not in self.reg.entities:
            raise AtlasBaseException(AtlasErrorCode.UNKNOWN_TYPENAME, type_name)
        types = sorted(self.reg.entities[type_name].type_and_all_sub_types())
        filters: List[dict] = [{"terms": {"typeName": types}}, {"term": {"status": "ACTIVE"}}]
        if match != "fortype":
            for k, v in uattrs.items():
                f = f"idx.str.{k}"
                v = str(v)
                if match == "startswith":
                    filters.append({"prefix": {f: v}})
                elif match == "endswith":
                    filters.append({"wildcard": {f: "*" + v}})
                elif match == "contains":
                    filters.append({"wildcard": {f: "*" + v + "*"}})
                elif match == "matches":
                    filters.append({"regexp": {f: v}})
                else:
                    filters.append({"term": {f: v}})
        return [g async for g, _ in self.s.store.scan(self.s.store.entities, {"bool": {"filter": filters}},
                                                          source=["guid"])]

    def _is_lineage(self, type_name: str) -> bool:
        t = self.reg.entities.get(type_name)
        return bool(t and "Process" in t.all_super_types)

    def _related(self, entity: dict) -> List[dict]:
        out = []
        for v in (entity.get("relationshipAttributes") or {}).values():
            for x in (v if isinstance(v, list) else [v]):
                if isinstance(x, dict) and x.get("guid") and x.get("relationshipStatus", "ACTIVE") == "ACTIVE":
                    out.append(x)
        return out

    def _collect_types(self, entity: dict, acc: Dict[str, Set[str]]) -> None:
        reg = self.reg

        def add(name: str) -> None:
            name = base_type_name(name)
            cat = reg.category_of(name)
            if cat is None or name in acc.setdefault(cat, set()):
                return
            acc[cat].add(name)
            d = reg.get_def(name)
            for st in d.get("superTypes") or []:
                add(st)
            for a in d.get("attributeDefs") or []:
                bt = base_type_name(a.get("typeName", ""))
                if reg.category_of(bt) in (ENUM, STRUCT):
                    add(bt)
            if cat == RELATIONSHIP:
                add(d["endDef1"]["type"])
                add(d["endDef2"]["type"])
        add(entity["typeName"])
        for c in entity.get("classifications") or []:
            add(c["typeName"])
        for bm in (entity.get("businessAttributes") or {}):
            add(bm)
        for x in self._related(entity):
            if x.get("relationshipType") and x["relationshipType"] in reg.relationships \
                    and not reg.relationships[x["relationshipType"]].synthetic:
                add(x["relationshipType"])

    async def export(self, request: dict, user: str, client_ip: str = "") -> Tuple[bytes, dict]:
        items = request.get("itemsToExport") or []
        options = request.get("options") or {}
        fetch = str(options.get("fetchType") or "full").lower()
        skip_lineage = str(options.get("skipLineage", "false")).lower() == "true"
        try:
            change_marker = int(options.get("changeMarker") or 0) if fetch == "incremental" else 0
        except (TypeError, ValueError):
            change_marker = 0
        start = now_ms()
        order: List[str] = []
        entities: Dict[str, dict] = {}
        types: Dict[str, Set[str]] = {}
        metrics: Dict[str, int] = {}
        statuses = []
        processed: Set[str] = set()
        direction: Dict[str, str] = {}
        for item in items:
            try:
                queue = await self._start_guids(item, options)
                if not queue:
                    statuses.append("FAIL")
                    continue
                # incremental export of a hive_table follows "connected" semantics, otherwise "full" (Atlas)
                connected = fetch == "connected"
                if fetch == "incremental":
                    first = await self.s.store.get(self.s.store.entities, queue[0])
                    connected = bool(first) and first.get("typeName") == "hive_table"
                lineage_queue: List[str] = []
                while queue or lineage_queue:
                    if not queue:
                        queue, lineage_queue = lineage_queue, []
                    guid = queue.pop(0)
                    if guid in processed:
                        continue
                    processed.add(guid)
                    try:
                        ext = await self.s.entities.get_by_guid(guid)
                    except AtlasBaseException:
                        continue
                    e = ext["entity"]
                    qualifies = not change_marker or int(e.get("updateTime") or 0) >= change_marker
                    if guid not in entities and qualifies:
                        entities[guid] = ext
                        order.append(guid)
                        metrics[f"entity:{e['typeName']}"] = metrics.get(f"entity:{e['typeName']}", 0) + 1
                        metrics["entity:withExtInfo"] = metrics.get("entity:withExtInfo", 0) + 1
                    self._collect_types(e, types)
                    for ref in (ext.get("referredEntities") or {}).values():
                        processed.add(ref["guid"])
                        self._collect_types(ref, types)
                        if qualifies:
                            metrics[f"entity:{ref['typeName']}"] = metrics.get(f"entity:{ref['typeName']}", 0) + 1
                        elif int(ref.get("updateTime") or 0) >= change_marker and ref["guid"] not in entities:
                            # incremental: modified referred entities of an unmodified entity are exported alone
                            entities[ref["guid"]] = {"entity": ref, "referredEntities": {}}
                            order.append(ref["guid"])
                            metrics[f"entity:{ref['typeName']}"] = metrics.get(f"entity:{ref['typeName']}", 0) + 1
                    cur = direction.get(guid)
                    if cur is not None and self._is_lineage(e["typeName"]):
                        cur = "OUTWARD"
                    for x in self._related(e):
                        lin = self._is_lineage(x.get("typeName", ""))
                        if skip_lineage and lin:
                            continue
                        if connected:
                            rt = self.reg.relationships.get(x.get("relationshipType") or "")
                            edge_dir = "OUTWARD" if rt is not None and rt.end1.type == e["typeName"] else "INWARD"
                            dirs = [edge_dir] if cur is None else [cur]
                            if cur is not None:
                                is_lin_entity = self._is_lineage(e["typeName"])
                                if (not is_lin_entity and cur != edge_dir) or (is_lin_entity and cur == edge_dir):
                                    continue
                            prev = direction.get(x["guid"])
                            if prev is None:
                                direction[x["guid"]] = dirs[0]
                            elif prev == "OUTWARD" and dirs[0] == "INWARD":
                                direction[x["guid"]] = "INWARD"
                                processed.discard(x["guid"])
                            else:
                                continue
                        elif x["guid"] in processed:
                            continue
                        (lineage_queue if lin else queue).append(x["guid"])
                statuses.append("SUCCESS")
            except AtlasBaseException as ex:
                log.warning("export of %s failed: %s", item, ex.message)
                statuses.append("FAIL")
        typesdef = {k: [] for k in CATEGORY_LIST_KEYS.values()}
        for cat, names in types.items():
            for n in sorted(names):
                d = copy.deepcopy(self.reg.get_def(n))
                if cat == ENTITY:
                    d = self.reg.api_def(n)
                typesdef[CATEGORY_LIST_KEYS[cat]].append(d)
        status = "FAIL" if not statuses else statuses[0]
        if any(x != status for x in statuses):
            status = "PARTIAL_SUCCESS"
        end = now_ms()
        metrics["duration"] = end - start
        result = {"request": request, "userName": user, "clientIpAddress": client_ip, "hostName": socket.gethostname(),
                  "timeStamp": start, "metrics": metrics, "operationStatus": status,
                  "sourceClusterName": self.s.settings.server_name, "changeMarker": start}
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for g in order:
                z.writestr(f"{g}.json", json.dumps(entities[g]))
            z.writestr(ORDER, json.dumps(order))
            z.writestr(TYPES, json.dumps(typesdef))
            z.writestr(INFO, json.dumps(result))
        await self.s.audits.add("EXPORT", user, json.dumps(request), ",".join(order), len(order), start, end, client_ip)
        if order:   # Atlas writes the export/import audit entry only when there is data
            await self.s.audits.add_expimp(user, "EXPORT", json.dumps(options), json.dumps(result), start, end,
                                           self.s.settings.server_name,
                                           server_name_from_full_name(options.get("replicatedTo")) or "")
        if status != "FAIL":
            with import_in_progress():   # server bookkeeping is not subject to the user's entity privileges
                await self.s.servers.record(options.get("replicatedTo"), order, "replicatedTo", result["changeMarker"],
                                            _is_true(options.get("skipUpdateReplicationAttr")), user)
        return buf.getvalue(), result

    # ================================================================== import
    async def import_zip(self, data: bytes, request: Optional[dict], user: str, client_ip: str = "",
                         progress=None, abort: Optional[asyncio.Event] = None) -> dict:
        # like Atlas (RequestContext.importInProgress): admin-import was verified by the caller, the
        # entity/type/relationship checks are skipped for the imported content
        with import_in_progress():
            async with self.s.store.deferred_refresh(), self.s.entities.deferred_propagation(user):
                return await self._import_zip(data, request, user, client_ip, progress, abort)

    async def _import_zip(self, data: bytes, request: Optional[dict], user: str, client_ip: str = "",
                          progress=None, abort: Optional[asyncio.Event] = None) -> dict:
        request = request or {}
        options = request.get("options") or {}
        start = now_ms()
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, "import data is not a valid zip file")
        check_zip(z, self.s.settings.max_import_uncompressed_mb * 1024 * 1024, "import ZIP")
        names = set(z.namelist())
        order: List[str] = json.loads(z.read(ORDER)) if ORDER in names else \
            [n[:-5] for n in sorted(names) if n.endswith(".json") and n not in (INFO, TYPES)]
        export_result = json.loads(z.read(INFO)) if INFO in names else {}
        metrics: Dict[str, int] = {}
        export_items = ((export_result.get("request") or {}).get("itemsToExport")) or []
        new_classifications: Set[str] = set()
        transforms = ImportTransforms.from_option(options.get("transforms"))
        if transforms is not None:
            transforms.shape(self.reg, export_items, new_classifications.add)
        transformers = EntityTransformers.from_option(options.get("transformers"), self.reg, export_items,
                                                      new_classifications.add)
        # --- types
        if TYPES in names and str(options.get("updateTypeDefinition", "true")).lower() != "false":
            await self._import_types(json.loads(z.read(TYPES)), user, metrics)
        # --- entities
        start_guid = options.get("startGuid")
        if start_guid and start_guid in order:
            order = order[order.index(start_guid):]
        elif options.get("startPosition") not in (None, ""):
            try:
                order = order[max(0, int(options["startPosition"])):]
            except (TypeError, ValueError):
                raise AtlasBaseException(AtlasErrorCode.INVALID_PARAMETERS, "startPosition must be a number")
        missing_cls = sorted(c for c in new_classifications if c and c not in self.reg.classifications)
        if missing_cls:
            await self.s.typedefs.create({"classificationDefs": [{"name": c} for c in missing_cls]}, user)
        guid_map: Dict[str, str] = {}
        exts: List[dict] = []
        for g in order:
            n = f"{g}.json"
            if n in names:
                exts.append(json.loads(z.read(n)))
        all_entities: List[dict] = []
        for ext in exts:
            all_entities.append(ext["entity"])
            all_entities.extend((ext.get("referredEntities") or {}).values())
        for e in all_entities:
            if transforms is not None:
                transforms.apply(e)
            if transformers is not None:
                transformers.apply(e)
        processed: List[str] = []
        failures: Dict[str, str] = {}
        total = len(all_entities)
        # pass 1: attributes, classifications, labels, business metadata
        for i, e in enumerate(all_entities):
            if abort is not None and abort.is_set():
                break
            et = self.reg.entities.get(e.get("typeName"))
            if et is None:
                failures[e.get("guid", "?")] = f"unknown type {e.get('typeName')}"
                continue
            plain = {k: v for k, v in (e.get("attributes") or {}).items()
                     if k in et.attributes and not et.attributes[k].is_object_ref}
            ent = {"typeName": e["typeName"], "guid": e["guid"], "attributes": plain,
                   "classifications": [c for c in e.get("classifications") or []
                                       if c.get("entityGuid") in (None, e["guid"])],
                   "labels": e.get("labels") or [], "customAttributes": e.get("customAttributes"),
                   "businessAttributes": e.get("businessAttributes"), "homeId": e.get("homeId"),
                   "provenanceType": e.get("provenanceType", 0)}
            try:
                res = await self.s.entities.create_or_update({"entity": ent}, user, replace_classifications=True,
                                                            replace_business_attributes=True)
                new_guid = (res.get("guidAssignments") or {}).get(e["guid"], e["guid"])
                guid_map[e["guid"]] = new_guid
                for op, hs in (res.get("mutatedEntities") or {}).items():
                    key = f"entity:{e['typeName']}:{'created' if op == 'CREATE' else 'updated'}"
                    metrics[key] = metrics.get(key, 0) + len(hs)
                processed.append(new_guid)
            except AtlasBaseException as ex:
                failures[e["guid"]] = ex.message
            if progress:
                await progress(i + 1, total, len(failures))
        # pass 2: relationships (relationship attributes and legacy reference attributes)
        for e in all_entities:
            if e["guid"] not in guid_map:
                continue
            et = self.reg.entities.get(e["typeName"])
            rel: Dict[str, Any] = {}
            src = dict(e.get("relationshipAttributes") or {})
            for k, v in (e.get("attributes") or {}).items():
                if k in et.attributes and et.attributes[k].is_object_ref and k not in src:
                    src[k] = v
            for k, v in src.items():
                if k not in et.relationship_attributes:
                    continue
                items = v if isinstance(v, list) else ([v] if v else [])
                refs = []
                for x in items:
                    if not isinstance(x, dict) or x.get("relationshipStatus", "ACTIVE") != "ACTIVE":
                        continue
                    tg = guid_map.get(x.get("guid"), x.get("guid"))
                    exists = tg in guid_map.values() or await self.s.store.get(self.s.store.entities, tg or "-") is not None
                    if not exists:
                        continue
                    ref = {"guid": tg, "typeName": x.get("typeName")}
                    if x.get("relationshipType"):
                        ref["relationshipType"] = x["relationshipType"]
                    if (x.get("relationshipAttributes") or {}).get("attributes"):
                        ref["relationshipAttributes"] = {"attributes": x["relationshipAttributes"]["attributes"]}
                    refs.append(ref)
                if not refs:
                    continue
                if isinstance(v, list):
                    rel[k] = refs
                else:
                    rel[k] = refs[0]
            if rel:
                try:
                    await self.s.entities.create_or_update(
                        {"entity": {"typeName": e["typeName"], "guid": guid_map[e["guid"]], "relationshipAttributes": rel}},
                        user, append_relationships=True)
                except AtlasBaseException as ex:
                    failures[e["guid"]] = ex.message
        # entities that were deleted in the source stay deleted
        deleted = [guid_map[e["guid"]] for e in all_entities if e.get("status") == "DELETED" and e["guid"] in guid_map]
        if deleted:
            try:
                await self.s.entities.delete_by_guids(deleted, user)
            except AtlasBaseException:
                pass
        end = now_ms()
        metrics["duration"] = end - start
        status = "SUCCESS" if not failures else ("PARTIAL_SUCCESS" if processed else "FAIL")
        export_result.pop("data", None)
        result = {"request": request, "userName": user, "clientIpAddress": client_ip, "hostName": socket.gethostname(),
                  "timeStamp": start, "metrics": metrics, "processedEntities": processed, "operationStatus": status,
                  "exportResultWithoutData": export_result}
        if failures:
            result["failures"] = failures
        await self.s.audits.add("IMPORT", user, json.dumps(options), ",".join(processed), len(processed), start, end, client_ip)
        if processed:
            await self.s.audits.add_expimp(user, "IMPORT", json.dumps(options), json.dumps(result), start, end,
                                           server_name_from_full_name(options.get("replicatedFrom"))
                                           or export_result.get("sourceClusterName") or "",
                                           self.s.settings.server_name)
        if status != "FAIL":
            await self.s.servers.record(options.get("replicatedFrom"), processed, "replicatedFrom",
                                        int(export_result.get("changeMarker") or 0),
                                        _is_true(options.get("skipUpdateReplicationAttr")), user)
        return result

    async def _import_types(self, typesdef: dict, user: str, metrics: Dict[str, int]) -> None:
        reg = self.reg
        to_create = {k: [] for k in CATEGORY_LIST_KEYS.values()}
        to_update = {k: [] for k in CATEGORY_LIST_KEYS.values()}
        for key in CATEGORY_LIST_KEYS.values():
            for d in typesdef.get(key) or []:
                cur = reg.get_def(d.get("name"))
                d = {k: v for k, v in d.items() if k not in ("subTypes", "relationshipAttributeDefs", "businessAttributeDefs")}
                if cur is None:
                    to_create[key].append(d)
                    metrics[f"typedef:{key[:-4]}"] = metrics.get(f"typedef:{key[:-4]}", 0) + 1
                elif key in ("entityDefs", "structDefs", "classificationDefs", "businessMetadataDefs"):
                    have = {a["name"] for a in cur.get("attributeDefs") or []}
                    extra = [a for a in d.get("attributeDefs") or [] if a["name"] not in have]
                    if extra:
                        upd = copy.deepcopy(cur)
                        upd["attributeDefs"] = list(upd.get("attributeDefs") or []) + extra
                        to_update[key].append(upd)
                elif key == "enumDefs":
                    have = {e["value"] for e in cur.get("elementDefs") or []}
                    extra = [e for e in d.get("elementDefs") or [] if e["value"] not in have]
                    if extra:
                        upd = copy.deepcopy(cur)
                        upd["elementDefs"] = list(upd.get("elementDefs") or []) + extra
                        to_update[key].append(upd)
        if any(to_create.values()):
            await self.s.typedefs.create(to_create, user)
        if any(to_update.values()):
            await self.s.typedefs.update(to_update, user)
