from typing import Optional

from aiocache import cached

from ...entities import LineageDirection, LineageInfo
from ..core import atlas_get

BASE_PATH = "v2/lineage"


@cached()
async def get_lineage_by_guid(guid: str, depth: int = 3, direction: LineageDirection = LineageDirection.BOTH, access_token: Optional[str] = None):
    """
    Fetch the lineage of an entity given its `guid`.

    Options:
    * You can use `depth` to specify the maximum number of hops to traverse the lineage graph. Default is 3.
    * You can use `direction` to specify whether to retrieve input lineage, output lineage or both. Default is both.
    * You can optionally provide an access token for the request.


    Exceptions:
    * Raises a `400` error if the query parameters are not valid.
    * Raises a `404` error if no lineage is found for the given entity.
    """

    path = f"{BASE_PATH}/{guid}"

    params = {
        "depth": depth,
        "direction": direction.value
    }

    response: str = await atlas_get(
        path=path,
        params=params,
        access_token=access_token
    )

    return LineageInfo.from_json(response)
# END get_lineage_by_guid
