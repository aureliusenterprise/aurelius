from typing import List, Optional

from aiocache import cached

from ...entities import EntityHeader, SearchResult
from ..core import atlas_get

PATH = "v2/search/basic"


@cached()
async def get_entities_by_type_name(type_name: str, limit: int = 100, offset: int = 0, access_token: Optional[str] = None) -> List[EntityHeader]:
    """
    API to search for all entities whose type matches the given `type_name`.
    Please note that the search only returns entity *headers*. 
    An entity header references the `guid` and `type_name` of the actual entity. 
    These can then be used to query the entities API.
    """

    entities: List[EntityHeader] = []

    # The search API returns paginated results. Retrieve pages until the page is empty.
    while True:

        params = {
            "typeName": type_name,
            "limit": limit,
            "offset": offset
        }

        page_json: str = await atlas_get(path=PATH, params=params, access_token=access_token)
        page = SearchResult.from_json(page_json)

        if len(page.entities) == 0:
            break
        # END IF

        entities += page.entities
        offset += limit
    # END LOOP

    return entities
# END get_entities_by_type_name
