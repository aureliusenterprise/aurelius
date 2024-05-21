import json
from typing import Optional

from aiocache import cached

from ...entities import EntityAuditEvent
from ..core import atlas_get

PATH_TEMPLATE = "v2/entity/{entity_guid}/audit"


@cached()
async def get_entity_audit_events(
    entity_guid: str,
    access_token: Optional[str] = None
):
    """
    Fetch all audit events for an entity given its GUID.

    Optionally, you can filter on a particular action type, limit the number of events returned, or offset the history based on a particular event key.
    """

    path = PATH_TEMPLATE.format(entity_guid=entity_guid)

    response: str = await atlas_get(
        path=path,
        access_token=access_token
    )

    response = json.loads(response)

    return [EntityAuditEvent.from_dict(audit) for audit in response]
# END get_entity_audit_events
