import asyncio
from typing import Iterable

from ...entities import Entity
from .resolve_entity_header import resolve_entity_header


async def get_referred_entities(entity: Entity) -> Iterable[Entity]:

    """
    Returns all entities referneced by the given `entity`.
    """

    entity_references = (
        reference
        for reference in entity.get_referred_entities()
    )

    referred_entities_co = (
        resolve_entity_header(header)
        for header in entity_references
    )

    referred_entities = await asyncio.gather(*referred_entities_co)

    return referred_entities
# END get_referred_entities
