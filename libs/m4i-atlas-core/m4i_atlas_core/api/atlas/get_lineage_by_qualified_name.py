from typing import Optional

from aiocache import cached

from ...entities import LineageDirection, LineageInfo
from ..core import atlas_get

BASE_PATH = "v2/lineage/uniqueAttribute/type"


@cached()
async def get_lineage_by_qualified_name(qualified_name: str, type_name: str, depth: int = 3, direction: LineageDirection = LineageDirection.BOTH, access_token: Optional[str] = None):
    """
    Fetch the lineage of an entity given its `qualified_name` and `type_name`.

    Options:
    * You can use `depth` to specify the maximum number of hops to traverse the lineage graph. Default is 3.
    * You can use `direction` to specify whether to retrieve input lineage, output lineage or both. Default is both.

    Exceptions:
    * Raises a `400` error if the query parameters are not valid.
    * Raises a `404` error if no lineage is found for the given entity.
    """

    path = f"{BASE_PATH}/{type_name}"

    params = {
        "depth": depth,
        "direction": direction.value,
        "qualifiedName": qualified_name
    }

    response: str = await atlas_get(
        path=path,
        params=params,
        access_token=access_token
    )

    return LineageInfo.from_json(response)
# END get_lineage_by_qualified_name
