from typing import Optional

from aiocache import cached

from ...entities import TypesDef
from ..core import atlas_get

PATH = "v2/types/typedefs"


@cached()
async def get_type_defs(access_token: Optional[str] = None):

    response: str = await atlas_get(PATH, access_token=access_token)

    type_defs = TypesDef.from_json(response)

    return type_defs
# END get_type_defs
