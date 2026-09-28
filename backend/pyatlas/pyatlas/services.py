"""Service container wiring the store, type system, repository and discovery layers together."""
from __future__ import annotations

import os
import platform
import time
from typing import Any, Dict, Optional

from .config import Settings
from .discovery.lineage import LineageService
from .discovery.search import SavedSearchService, SearchService
from .downloads import DownloadManager
from .errors import AtlasBaseException, AtlasErrorCode
from .glossary.service import GlossaryService
from .repository.entity_store import EntityStore
from .store.es import EsStore
from .typesystem.registry import BUSINESS_METADATA, CLASSIFICATION, ENTITY, RELATIONSHIP

START = int(time.time() * 1000)


class Services:
    def __init__(self, es_client, settings: Settings):
        from .typesystem.typedef_store import TypeDefStore
        self.settings = settings
        self.store = EsStore(es_client, settings)
        self.typedefs = TypeDefStore(self.store, settings.typedef_cache_check_secs)
        from .authz import AuthzService, build_authorizer
        self.authz = AuthzService(build_authorizer(settings), self.typedefs)
        self.typedefs.authz = self.authz
        self.entities = EntityStore(self.store, self.typedefs, settings)
        self.entities.authz = self.authz
        self.search = SearchService(self.store, self.typedefs, self.entities, settings)
        self.saved = SavedSearchService(self.store)
        self.lineage = LineageService(self.store, self.typedefs, self.entities, settings)
        self.glossary = GlossaryService(self.entities)
        self.downloads = DownloadManager(settings.download_dir)
        from .admin.impexp import ExportImportService
        from .admin.service import (ActiveSearches, AdminAuditService, AsyncImportService, MetricsStatsService,
                                    RequestMetrics, TaskStore)
        self.audits = AdminAuditService(self.store)
        self.tasks = TaskStore(self.store)
        self.impexp = ExportImportService(self)
        from .admin.replication import AtlasServerService
        self.servers = AtlasServerService(self)
        self.metrics_stats = MetricsStatsService(self)
        self.async_imports = AsyncImportService(self)
        self.request_metrics = RequestMetrics()
        self.active_searches = ActiveSearches()

    async def start(self) -> None:
        await self.store.bootstrap()
        await self.typedefs.load()
        if self.settings.load_models:
            await self.typedefs.load_models(self.settings.models_dir)
        now = int(time.time() * 1000)
        await self.audits.add("SERVER_START", "admin", self.settings.server_name, "", 0, now, now)
        await self.import_on_start()
        self.metrics_stats.start_scheduler()

    async def import_on_start(self) -> None:
        """Import the ZIPs of ``PYATLAS_IMPORT_ON_START`` / ``--import-zip`` that were not imported before."""
        import hashlib
        import logging
        from pathlib import Path
        log = logging.getLogger("pyatlas.import")
        for raw in (p.strip() for p in (self.settings.import_on_start or "").split(",")):
            if not raw:
                continue
            path = Path(raw)
            if not path.is_file():
                log.warning("import-on-start: %s not found", path)
                continue
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            key = f"imported_zip:{digest}"
            if (self.settings.import_on_start_mode or "once").lower() != "always" and \
                    await self.store.get(self.store.meta, key) is not None:
                log.info("import-on-start: %s was already imported, skipping", path.name)
                continue
            log.info("import-on-start: importing %s ...", path.name)
            t0 = time.time()
            res = await self.impexp.import_zip(data, {"options": {"fileName": str(path)}}, "admin")
            log.info("import-on-start: %s: %s, %d entities in %.1fs", path.name, res["operationStatus"],
                     len(res.get("processedEntities") or []), time.time() - t0)
            if res["operationStatus"] != "FAIL":
                await self.store.put(self.store.meta, key, {"kind": "system", "name": key, "updateTime": int(time.time() * 1000),
                                                            "value": {"file": path.name, "status": res["operationStatus"]}})

    async def stop(self) -> None:
        self.metrics_stats.stop()
        await self.downloads.wait_all()
        await self.async_imports.wait_all()

    async def type_has_instances(self, name: str, category: str) -> bool:
        s = self.store
        if category == ENTITY:
            return await s.count(s.entities, {"term": {"typeName": name}}) > 0
        if category == CLASSIFICATION:
            return await s.count(s.entities, {"term": {"allClassificationNames": name}}) > 0
        if category == RELATIONSHIP:
            return await s.count(s.relationships, {"term": {"typeName": name}}) > 0
        if category == BUSINESS_METADATA:
            return await s.count(s.entities, {"exists": {"field": f"bmidx.str.{name}"}}) > 0 or \
                await s.count(s.entities, {"exists": {"field": f"bmidx.lng.{name}"}}) > 0
        return False

    async def dsl_search(self, query: str, type_name: Optional[str], classification: Optional[str],
                         limit: int, offset: int) -> dict:
        from .discovery.dsl import DslExecutor
        return await DslExecutor(self).execute(query, type_name, classification, limit, offset)

    async def metrics(self) -> Dict[str, Any]:
        s = self.store
        reg = self.typedefs.registry

        async def agg(status: str, field: str = "typeName") -> Dict[str, int]:
            q = {"bool": {"filter": [{"term": {"status": status}}]}} if status else {"match_all": {}}
            r = await s.search(s.entities, q, size=0, aggs={"a": {"terms": {"field": field, "size": 5000}}})
            return {b["key"]: b["doc_count"] for b in r.get("aggregations", {}).get("a", {}).get("buckets", [])}
        active = await agg("ACTIVE")
        deleted = await agg("DELETED")
        tags = await agg("ACTIVE", "allClassificationNames")
        shell_q = {"bool": {"filter": [{"term": {"isIncomplete": True}}]}}
        r = await s.search(s.entities, shell_q, size=0, aggs={"a": {"terms": {"field": "typeName", "size": 5000}}})
        shell = {b["key"]: b["doc_count"] for b in r.get("aggregations", {}).get("a", {}).get("buckets", [])}

        def incl_sub(counts: Dict[str, int]) -> Dict[str, int]:
            out = {}
            for t, et in reg.entities.items():
                n = sum(counts.get(x, 0) for x in et.type_and_all_sub_types())
                if n:
                    out[t] = n
            return out
        used = set(active) | set(deleted)
        now = int(time.time() * 1000)
        return {
            "data": {
                "general": {
                    "collectionTime": now,
                    "entityCount": sum(active.values()) + sum(deleted.values()),
                    "tagCount": len(reg.classifications),
                    "typeUnusedCount": len([t for t in reg.entities if t not in used]),
                    "typeCount": len(reg.entities),
                    "stats": {
                        "Server:startTimeStamp": START, "Server:activeTimeStamp": START,
                        "Server:upTime": f"{(now - START) // 1000} seconds",
                        "Server:statusBackendStore": "ACTIVE", "Server:statusIndexStore": "ACTIVE",
                    },
                },
                "entity": {
                    "entityActive": active, "entityDeleted": deleted, "entityShell": shell,
                    "entityActive-typeAndSubTypes": incl_sub(active),
                    "entityDeleted-typeAndSubTypes": incl_sub(deleted),
                    "entityShell-typeAndSubTypes": incl_sub(shell),
                },
                "tag": {"tagEntities": tags},
                "system": {
                    "os": {"os.name": platform.system(), "os.version": platform.release(),
                           "os.arch": platform.machine(), "os.vcpus": os.cpu_count()},
                    "runtime": {"name": "CPython", "version": platform.python_version()},
                    "memory": {},
                },
            }
        }
