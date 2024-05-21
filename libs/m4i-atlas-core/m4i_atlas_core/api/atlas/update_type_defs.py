from typing import Optional

from ...entities import TypesDef
from ..core import atlas_put

PATH = "v2/types/typedefs"


async def update_type_defs(types: TypesDef, access_token: Optional[str] = None):

    """
    Bulk update API for all atlas type definitions. 
    Existing definitions will be overwritten.
    It does not create any new type definitions

    Returns a composite wrapper object with lists of type definitions that were successfully created.
    """

    response: str = await atlas_put(
        path=PATH,
        body=types.to_json(),
        access_token=access_token
    )

    type_defs = TypesDef.from_json(response)

    return type_defs
# END create_type_defs
