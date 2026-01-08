from typing import Optional

from ...api.atlas import get_entity_by_guid
from ...entities import Entity
from .get_all_connected_enteties import get_all_connected_entities


class MultipleParentsError(Exception):
    """Raised when an entity has multiple parents and choose_first_parent is False."""
    pass


async def get_breadcrumbs(
    entity: Entity, 
    choose_first_parent: bool = False,
    access_token: Optional[str] = None
) -> list[Entity]:
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
    breadcrumb: list[Entity] = [entity]
    
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
) -> dict[str, list[Entity]]:
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
    all_entities = await get_all_connected_entities(entity)
    
    result: dict[str, list[Entity]] = {}
    
    # Process entities in breadth-first order starting from the root entity
    queue: list[str] = [entity.guid]
    visited: set[str] = set()
    
    while queue:
        current_guid = queue.pop(0)
        
        # Skip if already visited
        if current_guid in visited:
            continue
        
        visited.add(current_guid)
        current_entity = all_entities[current_guid]
        
        # Get parent entities
        parent_object_ids = list(current_entity.get_parents())
        parent_guids = [obj_id.guid for obj_id in parent_object_ids if obj_id.guid]
        
        # Build breadcrumb for current entity
        if not parent_guids:
            # Root entity - breadcrumb is just itself
            breadcrumb = [current_entity]
        else:
            # Check for multiple parents
            if len(parent_guids) > 1 and not choose_first_parent:
                raise MultipleParentsError(
                    f"Entity {current_guid} has multiple parents {parent_guids}. "
                    "Set choose_first_parent=True to automatically select the first parent."
                )
            
            # Select which parent to follow
            selected_parent_guid = parent_guids[0]
            
            # Reuse parent's breadcrumb and append current entity
            if selected_parent_guid in result:
                # Parent already processed, reuse its breadcrumb
                breadcrumb = result[selected_parent_guid] + [current_entity]
            elif selected_parent_guid in all_entities:
                # Parent exists but not yet processed, compute its breadcrumb first
                parent_breadcrumb = _compute_breadcrumb_internal(
                    entity_guid=selected_parent_guid,
                    all_entities=all_entities,
                    choose_first_parent=choose_first_parent,
                    result=result
                )
                breadcrumb = parent_breadcrumb + [current_entity]
            else:
                # Parent not in connected entities, just start with current
                breadcrumb = [current_entity]
        
        result[current_guid] = breadcrumb
        
        # Add all children to queue
        child_object_ids = list(current_entity.get_children())
        for child_obj_id in child_object_ids:
            if child_obj_id.guid and child_obj_id.guid not in visited and child_obj_id.guid in all_entities:
                queue.append(child_obj_id.guid)
    
    return result


def _compute_breadcrumb_internal(
    entity_guid: str,
    all_entities: dict[str, Entity],
    choose_first_parent: bool,
    result: dict[str, list[Entity]]
) -> list[Entity]:
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
        breadcrumb = [current_entity]
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
            breadcrumb = parent_breadcrumb + [current_entity]
        else:
            # Parent not available, start with current
            breadcrumb = [current_entity]
    
    # Memoize result
    result[entity_guid] = breadcrumb
    return breadcrumb