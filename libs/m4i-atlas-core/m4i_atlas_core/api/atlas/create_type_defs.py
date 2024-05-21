from typing import Optional

from ...entities import TypesDef
from ..core import atlas_post

PATH = "v2/types/typedefs"


async def create_type_defs(types: TypesDef, access_token: Optional[str] = None):

    """
    Bulk create API for all atlas type definitions. 
    Only new definitions will be created. 
    Any changes to the existing definitions will be discarded.

    Returns a composite wrapper object with lists of type definitions that were successfully created.
    """

    response: str = await atlas_post(
        path=PATH,
        body=types.to_json(),
        access_token=access_token
    )

    type_defs = TypesDef.from_json(response)

    return type_defs
# END create_type_defs
