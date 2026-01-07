
import asyncio
import json
from typing import Dict, List, Optional

from aiocache import Cache
from aiohttp import ClientResponse

from ...entities import Entity
from ..core import atlas_get
from .get_entity_by_guid import get_entity_by_guid

BASE_PATH = "v2/entity/bulk"


def _batches(items: List[str], batch_size: int):
    """Generate batches of items with given batch size."""
    if items is None or batch_size <= 0:
        return []
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


async def _get_entity_by_guid_if_cached(
    guid: str,
    ignore_relationships: bool = True,
    min_ext_info: bool = True,
    access_token: Optional[str] = None
) -> Optional[Entity]:
    """
    Check if an entity is already cached from get_entity_by_guid.
    
    Returns the cached entity if available, otherwise None.
    """    
    # Get the cache instance used by get_entity_by_guid
    cache = Cache(Cache.MEMORY)
    # Build the cache key the same way aiocache does for get_entity_by_guid
    cache_key = f"get_entity_by_guid({guid}, {Entity}, {ignore_relationships}, {min_ext_info}, {access_token})"
    
    return await cache.get(cache_key)


def _get_future_fetch_entities_batch(
    batch: List[str],
    ignore_relationships: bool = True,
    min_ext_info: bool = True,
    access_token: Optional[str] = None
) -> asyncio.Future[Dict[str, Entity]]:
    """
    Create a future to fetch a batch of entities from Atlas.
    
    Returns a coroutine that will fetch and return a dictionary mapping GUIDs to Entity objects.
    """
    # Build query parameters
    params = {
        "guid": batch,
        "ignoreRelationships": ignore_relationships,
        "minExtInfo": min_ext_info
    }
    
    # Return the coroutine (future) without awaiting
    return atlas_get(
        path=BASE_PATH,
        params=json.dumps(params),
        parser=ClientResponse.json,
        access_token=access_token
    )


async def _parse_batch_response(response: dict) -> Dict[str, Entity]:
    """Parse entities from batch response."""
    result: Dict[str, Entity] = {}
    entities_list = response.get('entities', [])
    for entity_dict in entities_list:
        entity = Entity.from_dict(entity_dict)
        result[entity.guid] = entity
    return result


async def get_entities_by_guids(
    guids: List[str],
    ignore_relationships: bool = True,
    min_ext_info: bool = True,
    access_token: Optional[str] = None,
    batch_size: int = 50
) -> Dict[str, Entity]:
    """
    Fetch complete definition of entities with given GUIDs in batches.
    
    This function:
    1. Checks the cache for already-fetched entities from get_entity_by_guid
    2. Fetches uncached entities in batches of up to 50 GUIDs
    3. Returns a dictionary mapping GUIDs to Entity objects
    
    Args:
        guids: List of entity GUIDs to fetch
        ignore_relationships: Whether to ignore relationships in the response
        min_ext_info: Whether to minimize extended information
        access_token: Optional access token for authentication
        
    Returns:
        Dictionary mapping GUID strings to Entity objects
    """
    if not guids:
        return {}
    
    result: Dict[str, Entity] = {}
    guids_to_fetch: List[str] = []
    
    # Check which entities are already cached
    for guid in guids:
        cached_entity = await _get_entity_by_guid_if_cached(
            guid, ignore_relationships, min_ext_info, access_token
        )
        if cached_entity is not None:
            result[guid] = cached_entity
        else:
            guids_to_fetch.append(guid)
    
    # Fetch uncached entities in batches
    cache = Cache(Cache.MEMORY)
    
    # Await all batch requests concurrently
    batch_responses = await asyncio.gather(*(
        _get_future_fetch_entities_batch(batch, ignore_relationships, min_ext_info, access_token)
        for batch in _batches(guids_to_fetch, batch_size)
    ))
    
    # Process results and cache entities
    for response in batch_responses:
        batch_result = await _parse_batch_response(response)
        result.update(batch_result)
        
    # Cache fetched entities for future get_entity_by_guid calls
    for guid, entity in result.items():
        cache_key = f"get_entity_by_guid({guid}, {Entity}, {ignore_relationships}, {min_ext_info}, {access_token})"
        await cache.set(cache_key, entity)
    
    return result
