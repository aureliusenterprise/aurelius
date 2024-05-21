from typing import Optional

from ...entities import EntityMutationResponse
from ..core import atlas_delete

BASE_PATH = "v2/entity/guid"


async def delete_entity_soft(guid: str, access_token: Optional[str] = None):
    """
    Deletes an entity identified by its `guid`. 
    Rather than removing the entity from the database, this API sets the status of the entity to `DELETED`.
    """

    path = f"{BASE_PATH}/{guid}"

    response: str = await atlas_delete(path, access_token=access_token)

    mutations = EntityMutationResponse.from_json(response)

    return mutations
# END delete_entity_soft
