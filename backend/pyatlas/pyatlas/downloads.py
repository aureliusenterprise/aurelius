"""Background file generation for search-result and glossary exports.

Mirrors Atlas' ``*/download/create_file`` + ``download/status`` + ``download/{filename}``
flow: a request queues a task, the file is written to ``<download_dir>/<kind>/<user>/``
and the status endpoint lists pending tasks plus finished files of the current user.

Files live on the local disk of the node that generated them (like Atlas); behind a load
balancer use sticky sessions or a shared ``PYATLAS_DOWNLOAD_DIR``.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Awaitable, Callable, Dict, List

from .errors import AtlasBaseException, AtlasErrorCode

log = logging.getLogger(__name__)

MAX_PENDING_TASKS = 50
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_.@\-]+$")


class DownloadManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.tasks: Dict[str, dict] = {}
        self._background: set = set()

    def _dir(self, kind: str, user: str) -> Path:
        safe_user = re.sub(r"[^A-Za-z0-9_.@\-]", "_", user or "anonymous")
        return self.base_dir / kind / safe_user

    def submit(self, kind: str, user: str, file_name: str,
               writer: Callable[[Path], Awaitable[None]]) -> dict:
        pending = [t for t in self.tasks.values() if t["kind"] == kind and t["status"] in ("PENDING", "IN_PROGRESS")]
        if len(pending) > MAX_PENDING_TASKS:
            raise AtlasBaseException(AtlasErrorCode.PENDING_TASKS_ALREADY_IN_PROGRESS, len(pending))
        task = {"guid": str(uuid.uuid4()), "kind": kind, "status": "PENDING", "fileName": file_name,
                "createdBy": user, "createdTime": int(time.time() * 1000), "startTime": None}
        self.tasks[task["guid"]] = task

        async def run():
            task["status"] = "IN_PROGRESS"
            task["startTime"] = int(time.time() * 1000)
            d = self._dir(kind, user)
            d.mkdir(parents=True, exist_ok=True)
            tmp = d / (file_name + ".part")
            try:
                await writer(tmp)
                if tmp.exists():
                    os.replace(tmp, d / file_name)
                task["status"] = "COMPLETE"
            except Exception:
                log.exception("download task %s failed", file_name)
                task["status"] = "FAILED"
                if tmp.exists():
                    tmp.unlink()
            finally:
                # completed tasks are reported through the files on disk
                if task["status"] == "COMPLETE":
                    self.tasks.pop(task["guid"], None)
        t = asyncio.get_running_loop().create_task(run())
        self._background.add(t)
        t.add_done_callback(self._background.discard)
        return task

    async def wait_all(self) -> None:
        if self._background:
            await asyncio.gather(*list(self._background), return_exceptions=True)

    def status(self, kind: str, user: str) -> dict:
        records: List[dict] = []
        for t in self.tasks.values():
            if t["kind"] == kind and t["createdBy"] == user:
                records.append({"status": t["status"], "fileName": t["fileName"], "createdBy": t["createdBy"],
                                "createdTime": t["createdTime"], "startTime": t["startTime"]})
        d = self._dir(kind, user)
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.is_file() and not f.name.endswith(".part"):
                    st = f.stat()
                    records.append({"status": "COMPLETE", "fileName": f.name, "createdBy": user,
                                    "createdTime": int(st.st_mtime * 1000)})
        return {"searchDownloadRecords": records}

    def resolve(self, kind: str, user: str, file_name: str) -> Path:
        if not file_name or not _SAFE_NAME.match(file_name) or ".." in file_name:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"invalid file name {file_name}")
        return self._dir(kind, user) / file_name
