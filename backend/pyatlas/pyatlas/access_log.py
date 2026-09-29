"""Access log: who used pyatlas when (``<prefix>_access``, shown in Kibana as "logins per day").

pyatlas has no login step for most users: the Aurelius frontend logs in at Keycloak and sends access tokens.  A
"login" is therefore recorded per session:

* ``keycloak`` - the first request with a token of a Keycloak session (token claim ``sid`` / ``session_state``);
  a service account without session counts once per client and day,
* ``form``     - a login through the Atlas UI login form (``/j_spring_security_check``),
* ``basic``    - other password logins (HTTP Basic, e.g. scripts), once per user and day.

Each document: ``user, timestamp (epoch ms), method, client (Keycloak client), ip, session, groups``.  The
document id is the session key, so several pyatlas nodes record a session once.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections import OrderedDict
from typing import Iterable, Optional

log = logging.getLogger("pyatlas.access")

_MAX_REMEMBERED = 50000


class AccessLog:
    def __init__(self, store):
        self.store = store
        self._seen: "OrderedDict[str, None]" = OrderedDict()

    @staticmethod
    def _day(now: float) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime(now))

    def key_for_token(self, claims: dict, user: str) -> str:
        sid = claims.get("sid") or claims.get("session_state")
        if sid:
            return f"keycloak:{sid}"
        return f"keycloak:{claims.get('azp') or '-'}:{user}:{self._day(time.time())}"

    async def record(self, user: str, method: str, key: Optional[str] = None, client: Optional[str] = None,
                     ip: Optional[str] = None, groups: Iterable[str] = ()) -> None:
        now = time.time()
        if key is None:
            key = f"{method}:{user}:{self._day(now)}" if method == "basic" else f"{method}:{uuid.uuid4()}"
        if key in self._seen:
            return
        self._seen[key] = None
        while len(self._seen) > _MAX_REMEMBERED:
            self._seen.popitem(last=False)
        doc = {"user": user, "timestamp": int(now * 1000), "method": method, "client": client, "ip": ip,
               "session": key, "groups": sorted(set(groups))}
        try:
            await self.store.put(self.store.access, key, doc, create=True, refresh="false")
        except Exception as e:  # noqa: BLE001 - an existing document (other node) or ES trouble: never fail a request
            if "conflict" not in type(e).__name__.lower() and "409" not in str(e):
                log.warning("could not record the access of %s: %s", user, e)
