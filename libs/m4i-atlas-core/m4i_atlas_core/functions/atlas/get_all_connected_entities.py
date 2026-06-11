from typing import Dict, Optional

from ...entities import Entity
from ...api.atlas.get_entities_by_guids import get_entities_by_guids


async def get_all_connected_entities(entity: Entity, access_token: Optional[str] = None) -> Dict[str, Entity]:
    """
    Returns all entities conntected to the given `entity` by references as a dictionary mapping each entity by their respective guid.
    """
    connected_entities = {
        entity.guid: entity
    }

    entities_guids_to_visit = [
        e.guid
        for e in entity.get_parents() + entity.get_children()
        if e.guid not in connected_entities
    ]

    while entities_guids_to_visit:
        visited_entities = await get_entities_by_guids(
            guids=entities_guids_to_visit,
            ignore_relationships=False,
            access_token=access_token
        )

        connected_entities = {
            **connected_entities,
            **visited_entities
        }

        entities_guids_to_visit = [
            e.guid
            for visited_entity in visited_entities.values()
            for e in visited_entity.get_parents() + visited_entity.get_children()
            if e.guid not in connected_entities
        ]

    return connected_entities