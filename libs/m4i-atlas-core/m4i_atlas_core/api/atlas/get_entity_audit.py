import json

from typing import Optional

from aiocache import cached

from ...entities import EntityAuditEvent
from ..core import atlas_get

BASE_PATH = "v2/entity"
    

@cached()
async def get_entity_audit(entity_guid: str, offset: int = 0, count: int = 1, sort_by: str = "timestamp", sort_order: str = "desc", access_token: Optional[str] = None):
    PATH = f"{BASE_PATH}/{entity_guid}/audit?offset={offset}&count={count}&sortBy={sort_by}&sortOrder={sort_order}"
    response: str = await atlas_get(PATH, access_token=access_token)
    
    response = json.loads(response)

    if len(response) >= 1:
        audit = response[0]
        return EntityAuditEvent.from_dict(audit)

# END get_entity_audit
