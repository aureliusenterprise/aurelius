from typing import Dict, Iterable

from ...entities import Entity
from .get_referred_entities import get_referred_entities


async def get_all_referred_entities(entities: Iterable[Entity]) -> Dict[str, Entity]:

    """
    Returns all entities referenced by the given `entities` as a dictionary mapping each entity by their respective guid.
    """

    referred_entities = (
        referred_entity
        for entity in entities
        for referred_entity in await get_referred_entities(entity)
    )

    return {
        referred_entity.guid: referred_entity
        async for referred_entity in referred_entities
    }
# END get_referred_entities
