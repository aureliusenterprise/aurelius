from typing import Optional, TypeVar

from ...api import get_entities_by_attribute
from ...entities import Entity
from .resolve_entity_header import resolve_entity_header

T = TypeVar('T', bound=Entity)


async def get_entity_by_qualified_name(qualified_name: str, type_name: str) -> Optional[T]:

    search_result = await get_entities_by_attribute(
        attribute_name='qualifiedName',
        attribute_value=qualified_name,
        type_name=type_name
    )

    if len(search_result.entities) == 0:
        return None
    # END IF

    if len(search_result.entities) > 1:
        raise ValueError(
            """
            Multiple entities found for the given qualified name.

            Please provide a more specific qualified name.
            """
        )
    # END IF

    entity: T = await resolve_entity_header(search_result.entities[0])

    return entity
# END get_entity_by_qualified_name
