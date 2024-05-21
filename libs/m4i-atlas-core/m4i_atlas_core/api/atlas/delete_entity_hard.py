import json
from typing import List, Optional

from ...entities import EntityMutationResponse
from ..core import atlas_put

PATH = "admin/purge"


async def delete_entity_hard(guid: List[str], access_token: Optional[str] = None):
    """
    API to purge the entity with the given `guid` from Atlas.
    This removes the entity from the database completely.

    It is possible to purge multiple entities at once by passing in multiple `guids`.

    This API requires elevated user permissions.
    """

    response: str = await atlas_put(
        path=PATH,
        body=json.dumps(guid),
        access_token=access_token
    )

    mutations = EntityMutationResponse.from_json(response)

    return mutations
# END delete_entity_hard
