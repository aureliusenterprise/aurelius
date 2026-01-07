from typing import Dict, Iterable

from ...entities import Entity
from .get_referred_entities import get_referred_entities
from .get_all_referred_entities import get_all_referred_entities
from ...api.atlas.get_entities_by_guids import get_entities_by_guids


async def get_all_connected_entities(entity: Entity) -> Dict[str, Entity]:
    """
    Returns all entities conntected to the given `entity` by references as a dictionary mapping each entity by their respective guid.
    """
    connected_entities = {
        entity.guid: entity
    }

    entities_guids_to_visit = [
        guid
        for guid in entity.get_referred_entities()
        if guid not in connected_entities
    ]

    while entities_guids_to_visit:
        visited_entities = await get_entities_by_guids(
            guids=entities_guids_to_visit
        )

        connected_entities = {
            **connected_entities,
            **visited_entities
        }

        entities_guids_to_visit = [
            guid
            for visited_entity in visited_entities.values()
            for guid in visited_entity.get_referred_entities()
            if guid not in connected_entities
        ]

    return connected_entities