"""Clickstream of the Aurelius frontend: how the application is used and how people move through it.

The frontend (``libs/services/clickstream``) reports every navigation of a logged-in user to
``POST /api/aurelius/repository/log`` (``{app, timestamp, url, userid}``).  The old back end saved the events in
its database; pyatlas stores them in ``<prefix>_clickstream`` (Kibana dashboard "Aurelius usage") and still
writes them as JSON log lines.  Each event is enriched so it can be analysed without joins:

* ``page``: the kind of page (``browse``, ``search results``, ``entity details``, ``create entity``, ...), ``path``
  without ids and query, ``query``: the search text of search result pages;
* ``entityGuid``, ``entityType``, ``entityName``: the entity of a details / edit page;
* ``session`` / ``step``: a visit is a run of events of one user without a pause longer than 30 minutes;
  ``previousPage`` and ``secondsOnPreviousPage`` link each event to the one before it in the visit, so the
  dashboard can show where people go next and how long they stay; ``entry`` marks the first page of a visit.

The user is the authenticated user; the ``userid`` the browser sends is not trusted.  Visits are tracked in
memory: several pyatlas nodes or a restart start a new visit for a user.
"""
from __future__ import annotations

import re
import time
import uuid
from collections import OrderedDict
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

SESSION_GAP_SECS = 30 * 60
_MAX_USERS = 20000
GUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

# first path segments of the Aurelius frontend -> readable page names
PAGES = {
    ("search",): "search", ("search", "browse"): "browse", ("search", "results"): "search results",
    ("search", "details"): "entity details", ("search", "create-entity"): "create entity",
    ("search", "edit-entity"): "edit entity", ("dashboards",): "dashboard", ("dashboards", "domains"): "dashboard",
}


def parse_url(url: str) -> Tuple[str, str, Optional[str], Optional[str]]:
    """(page, path with ids replaced by ``:id``, search query, entity guid) of a frontend URL."""
    parts = urlsplit(url or "")
    segments = [s for s in parts.path.split("/") if s]
    guid = next((s for s in segments if GUID.match(s)), None)
    path = "/" + "/".join(":id" if GUID.match(s) else s for s in segments)
    names = [s for s in segments if not GUID.match(s)]
    page = PAGES.get(tuple(names[:2])) or PAGES.get(tuple(names[:1])) or (path if names else "home")
    query = (parse_qs(parts.query).get("query") or [None])[0]
    return page, path, (query.strip() or None) if query else None, guid


class Clickstream:
    def __init__(self, store):
        self.store = store
        self._visits: "OrderedDict[str, dict]" = OrderedDict()

    @property
    def index(self) -> str:
        return self.store.index("clickstream")

    def _visit(self, user: str, now: float) -> Tuple[dict, bool]:
        v = self._visits.pop(user, None)
        new = v is None or now - v["last"] > SESSION_GAP_SECS
        if new:
            v = {"session": uuid.uuid4().hex, "step": 0, "last": now, "page": None, "path": None}
        self._visits[user] = v
        while len(self._visits) > _MAX_USERS:
            self._visits.popitem(last=False)
        return v, new

    async def record(self, user: str, app: Optional[str], url: str, client_ts: Optional[int] = None) -> dict:
        now = time.time()
        page, path, query, guid = parse_url(url)
        v, new = self._visit(user, now)
        doc: Dict[str, object] = {
            "user": user, "app": app, "timestamp": int(now * 1000), "clientTimestamp": client_ts,
            "url": (url or "")[:2000], "path": path[:500], "page": page, "query": query[:500] if query else None,
            "session": v["session"], "step": v["step"] + 1, "entry": new,
            "previousPage": None if new else v["page"], "previousPath": None if new else v["path"],
            "secondsOnPreviousPage": None if new else round(now - v["last"], 1),
            "entityGuid": guid, "entityType": None, "entityName": None,
        }
        if guid:
            try:
                d = (await self.store.mget(self.store.entities, [guid],
                                           source_includes=["typeName", "displayText"])).get(guid)
            except Exception:  # noqa: BLE001 - the event is stored anyway
                d = None
            if d:
                doc["entityType"], doc["entityName"] = d.get("typeName"), d.get("displayText")
        v.update(step=v["step"] + 1, last=now, page=page, path=path)
        await self.store.put(self.index, f"{v['session']}-{v['step']:05d}", doc, refresh="false")
        return doc
