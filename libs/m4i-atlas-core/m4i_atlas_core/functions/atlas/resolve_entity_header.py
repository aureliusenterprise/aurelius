from typing import TypeVar

from ...api import get_entity_by_guid
from ...entities import Entity, ObjectId

T = TypeVar('T', bound=Entity)


async def resolve_entity_header(header: ObjectId) -> T:

    entity = await get_entity_by_guid(header.guid, header.type_name)

    # If the guid is a placeholder, it will start with a -.
    # In that case, set the attributes of the returned entity to the given unique attributes
    if header.guid.startswith("-") and header.unique_attributes is not None:
        entity.attributes = header.unique_attributes
    # END IF

    return entity
# END resolve_entity_header
