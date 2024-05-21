from typing import Optional

from aiocache import cached

from ...entities import (FilterCriteria, Operator, SearchParameters,
                         SearchResult)
from ..core import atlas_post

PATH = "v2/search/basic"


@cached()
async def get_entities_by_attribute(
    attribute_name: str,
    attribute_value: str,
    type_name: str,
    access_token: Optional[str] = None
):
    """
    API to retrieve data for the specified attribute search query.

    Please note that the search only returns entity *headers*. 
    An entity header references the `guid` and `type_name` of the actual entity. 
    These can then be used to query the entities API.
    """

    params = SearchParameters(
        entity_filters=FilterCriteria(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            operator=Operator.EQ
        ),
        type_name=type_name
    )

    response: str = await atlas_post(
        path=PATH,
        body=params.to_json(),
        access_token=access_token
    )

    search_result = SearchResult.from_json(response)

    return search_result
# END get_entities_by_attribute
