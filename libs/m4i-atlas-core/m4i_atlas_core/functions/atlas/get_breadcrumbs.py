from typing import Dict, List, Optional

from ...api.atlas import get_entity_by_guid
from ...entities import Entity
from .get_all_connected_entities import get_all_connected_entities


class MultipleParentsError(Exception):
    """Raised when an entity has multiple parents and choose_first_parent is False."""
    pass


async def get_breadcrumbs(
    entity: Entity, 
    choose_first_parent: bool = False,
    access_token: Optional[str] = None
) -> List[Entity]:
    """
    Returns the breadcrumbs for the given entity.
    
    args:
        entity: The entity to get breadcrumbs for.
        choose_first_parent: If True, always chooses the first parent in case of multiple parents. 
                           If False, raises MultipleParentsError when multiple parents exist.
        access_token: Optional access token for API authentication.
    Returns:
        A list of Entity objects representing the breadcrumbs from the root to the given entity.
    Raises:
        MultipleParentsError: If an entity has multiple parents and choose_first_parent is False.
    """
    breadcrumb: List[Entity] = []
    
    current_entity = entity
    
    while True:
        parent_object_ids = list(current_entity.get_parents())
        
        if not parent_object_ids:
            break
        
        # Extract GUIDs from ObjectId objects
        parent_guids = [obj_id.guid for obj_id in parent_object_ids if obj_id.guid]
        
        if not parent_guids:
            break
        
        # Check for multiple parents
        if len(parent_guids) > 1 and not choose_first_parent:
            raise MultipleParentsError(
                f"Entity {current_entity.guid} has multiple parents {parent_guids}. "
                "Set choose_first_parent=True to automatically select the first parent."
            )
        
        # Select which parent to follow
        selected_guid = parent_guids[0]
        
        # Fetch the parent entity
        parent_entity = await get_entity_by_guid(
            guid=selected_guid,
            entity_type=Entity,
            access_token=access_token
        )
        
        breadcrumb.append(parent_entity)
        current_entity = parent_entity
    
    # Reverse to have root at the beginning
    breadcrumb.reverse()
    return breadcrumb


async def get_breadcrumbs_for_all_descendants(
    entity: Entity, 
    choose_first_parent: bool = False,
    access_token: Optional[str] = None
) -> Dict[str, List[Entity]]:
    """
    Returns the breadcrumbs for all descendants of the given entity.

    args:
        entity: The entity to get breadcrumbs for all descendants.
        choose_first_parent: If True, always chooses the first parent in case of multiple parents. 
                           If False, raises MultipleParentsError when multiple parents exist.
        access_token: Optional access token for API authentication.
    Returns:
        A dictionary mapping each descendant entity guid to its list of Entity objects representing 
        the breadcrumbs from the root to that entity.
    Raises:
        MultipleParentsError: If an entity has multiple parents and choose_first_parent is False.
    """
    # Fetch all connected entities upfront
    all_entities = await get_all_connected_entities(entity, access_token=access_token)
    
    result: Dict[str, List[Entity]] = {}
    
    # Compute breadcrumbs for all entities using recursive memoization
    # This ensures parents are always processed before children
    for entity_guid in all_entities.keys():
        if entity_guid not in result:
            _compute_breadcrumb_internal(
                entity_guid=entity_guid,
                all_entities=all_entities,
                choose_first_parent=choose_first_parent,
                result=result
            )
    
    return result


def _compute_breadcrumb_internal(
    entity_guid: str,
    all_entities: Dict[str, Entity],
    choose_first_parent: bool,
    result: Dict[str, List[Entity]]
) -> List[Entity]:
    """
    Internal helper to compute breadcrumb for an entity using already fetched entities.
    Uses recursion with memoization via the result dict.
    """
    # If already computed, return it
    if entity_guid in result:
        return result[entity_guid]
    
    current_entity = all_entities[entity_guid]
    
    # Get parent entities
    parent_object_ids = list(current_entity.get_parents())
    parent_guids = [obj_id.guid for obj_id in parent_object_ids if obj_id.guid]
    
    # Build breadcrumb
    if not parent_guids:
        # Root entity
        breadcrumb = []
    else:
        # Check for multiple parents
        if len(parent_guids) > 1 and not choose_first_parent:
            raise MultipleParentsError(
                f"Entity {entity_guid} has multiple parents {parent_guids}. "
                "Set choose_first_parent=True to automatically select the first parent."
            )
        
        # Select which parent to follow
        selected_parent_guid = parent_guids[0]
        
        if selected_parent_guid in all_entities:
            # Recursively compute parent's breadcrumb
            parent_breadcrumb = _compute_breadcrumb_internal(
                entity_guid=selected_parent_guid,
                all_entities=all_entities,
                choose_first_parent=choose_first_parent,
                result=result
            )
            breadcrumb = parent_breadcrumb + [all_entities[selected_parent_guid]]
        else:
            # Parent not available, start with current
            breadcrumb = [all_entities[selected_parent_guid]]
    
    # Memoize result
    result[entity_guid] = breadcrumb
    return breadcrumb