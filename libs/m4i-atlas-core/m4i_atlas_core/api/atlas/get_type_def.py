from typing import Optional

from aiocache import cached

from ...entities import EntityDef
from ..core import atlas_get

BASE_PATH = "v2/types/entitydef/name"
    

@cached()
async def get_type_def(input_type: str, access_token: Optional[str] = None):
    PATH = f"{BASE_PATH}/{input_type}"
    response: str = await atlas_get(PATH, access_token=access_token)
    
    type_defs = EntityDef.from_json(response)

    return type_defs
# END get_type_def
