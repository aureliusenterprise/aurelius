from typing import Optional

from ...api import get_entities_by_attribute
from ...entities import Entity
from .resolve_entity_header import resolve_entity_header


async def get_entity_by_qualified_name(
    qualified_name: str, type_name: str, access_token: Optional[str] = None
) -> Optional[Entity]:
    search_result = await get_entities_by_attribute(
        attribute_name="qualifiedName",
        attribute_value=qualified_name,
        type_name=type_name,
        access_token=access_token,
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

    entity: Entity = await resolve_entity_header(search_result.entities[0], access_token=access_token)  # type: ignore[reportGeneralTypeIssues]

    return entity


# END get_entity_by_qualified_name
