from typing import Dict, Optional

from ...entities import EntitiesWithExtInfo, Entity, EntityMutationResponse
from ..core import atlas_post

PATH = "v2/entity/bulk"


async def create_entities(*entities: Entity, referred_entities: Optional[Dict[str, Entity]] = None, access_token: Optional[str] = None):
    """
    Bulk API to create new entities or updates existing entities in Atlas.

    Existing entities are matched using their unique `guid` if supplied or by their unique attributes (e.g. `qualifiedName`).
    """

    if referred_entities is None:
        referred_entities = {}
    # END IF

    entities_with_ext_info = EntitiesWithExtInfo(
        entities=list(entities),
        referred_entities=referred_entities
    )

    response: str = await atlas_post(
        path=PATH,
        body=entities_with_ext_info.to_json(),
        access_token=access_token
    )

    mutations = EntityMutationResponse.from_json(response)

    return mutations
# END create_entities
