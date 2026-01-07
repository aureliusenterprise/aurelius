from unittest.mock import AsyncMock, patch

import pytest

from ...entities import Entity
from .get_all_connected_enteties import get_all_connected_entities


@pytest.mark.asyncio
async def test__get_all_connected_entities_single_entity_no_references():
    """Test with a single entity that has no references to other entities."""
    entity = Entity(guid="entity-1")
    
    with patch.object(entity, 'get_referred_entities', return_value=[]):
        result = await get_all_connected_entities(entity)
        
        assert len(result) == 1
        assert "entity-1" in result
        assert result["entity-1"] == entity


@pytest.mark.asyncio
async def test__get_all_connected_entities_with_single_reference():
    """Test with an entity that references one other entity."""
    entity = Entity(guid="entity-1")
    referenced_entity = Entity(guid="entity-2")
    
    with patch.object(entity, 'get_referred_entities', return_value=["entity-2"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(referenced_entity, 'get_referred_entities', return_value=[]):
        
        # Return entity based on input guids
        def get_entities_side_effect(guids):
            if "entity-2" in guids:
                return {"entity-2": referenced_entity}
            return {}
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity)
        
        assert len(result) == 2
        assert "entity-1" in result
        assert "entity-2" in result
        assert result["entity-1"] == entity
        assert result["entity-2"] == referenced_entity
        
        mock_get_entities.assert_called_once_with(guids=["entity-2"])


@pytest.mark.asyncio
async def test__get_all_connected_entities_with_multiple_references():
    """Test with an entity that references multiple other entities."""
    entity = Entity(guid="entity-1")
    referenced_entity_2 = Entity(guid="entity-2")
    referenced_entity_3 = Entity(guid="entity-3")
    
    with patch.object(entity, 'get_referred_entities', return_value=["entity-2", "entity-3"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(referenced_entity_2, 'get_referred_entities', return_value=[]), \
         patch.object(referenced_entity_3, 'get_referred_entities', return_value=[]):
        
        # Return entities based on input guids
        def get_entities_side_effect(guids):
            result = {}
            if "entity-2" in guids:
                result["entity-2"] = referenced_entity_2
            if "entity-3" in guids:
                result["entity-3"] = referenced_entity_3
            return result
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity)
        
        assert len(result) == 3
        assert "entity-1" in result
        assert "entity-2" in result
        assert "entity-3" in result
        assert result["entity-1"] == entity
        assert result["entity-2"] == referenced_entity_2
        assert result["entity-3"] == referenced_entity_3
        
        mock_get_entities.assert_called_once_with(guids=["entity-2", "entity-3"])


@pytest.mark.asyncio
async def test__get_all_connected_entities_with_nested_references():
    """Test with entities that have nested references (entity -> entity-2 -> entity-3)."""
    entity = Entity(guid="entity-1")
    referenced_entity_2 = Entity(guid="entity-2")
    referenced_entity_3 = Entity(guid="entity-3")
    
    with patch.object(entity, 'get_referred_entities', return_value=["entity-2"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(referenced_entity_2, 'get_referred_entities', return_value=["entity-3"]), \
         patch.object(referenced_entity_3, 'get_referred_entities', return_value=[]):
        
        # Return different entities based on input guids
        def get_entities_side_effect(guids):
            if guids == ["entity-2"]:
                return {"entity-2": referenced_entity_2}
            elif guids == ["entity-3"]:
                return {"entity-3": referenced_entity_3}
            return {}
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity)
        
        assert len(result) == 3
        assert "entity-1" in result
        assert "entity-2" in result
        assert "entity-3" in result
        assert result["entity-1"] == entity
        assert result["entity-2"] == referenced_entity_2
        assert result["entity-3"] == referenced_entity_3
        
        assert mock_get_entities.call_count == 2


@pytest.mark.asyncio
async def test__get_all_connected_entities_with_circular_references():
    """Test with circular references (entity-1 -> entity-2 -> entity-1)."""
    entity = Entity(guid="entity-1")
    referenced_entity_2 = Entity(guid="entity-2")
    
    with patch.object(entity, 'get_referred_entities', return_value=["entity-2"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(referenced_entity_2, 'get_referred_entities', return_value=["entity-1"]):
        
        # Return entity based on input guids
        def get_entities_side_effect(guids):
            if "entity-2" in guids:
                return {"entity-2": referenced_entity_2}
            return {}
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity)
        
        # Should still only have 2 entities and should not loop infinitely
        assert len(result) == 2
        assert "entity-1" in result
        assert "entity-2" in result
        assert result["entity-1"] == entity
        assert result["entity-2"] == referenced_entity_2
        
        # Should only call get_entities_by_guids once because entity-1 is already visited
        mock_get_entities.assert_called_once_with(guids=["entity-2"])


@pytest.mark.asyncio
async def test__get_all_connected_entities_with_complex_graph():
    """Test with a complex graph structure with multiple levels and cross-references."""
    entity_1 = Entity(guid="entity-1")
    entity_2 = Entity(guid="entity-2")
    entity_3 = Entity(guid="entity-3")
    entity_4 = Entity(guid="entity-4")
    entity_5 = Entity(guid="entity-5")
    
    # Structure:
    # entity-1 -> [entity-2, entity-3]
    # entity-2 -> [entity-4]
    # entity-3 -> [entity-4, entity-5]
    # entity-4 -> []
    # entity-5 -> []
    
    with patch.object(entity_1, 'get_referred_entities', return_value=["entity-2", "entity-3"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(entity_2, 'get_referred_entities', return_value=["entity-4"]), \
         patch.object(entity_3, 'get_referred_entities', return_value=["entity-4", "entity-5"]), \
         patch.object(entity_4, 'get_referred_entities', return_value=[]), \
         patch.object(entity_5, 'get_referred_entities', return_value=[]):
        
        # Return different entities based on input guids
        def get_entities_side_effect(guids):
            result = {}
            for guid in guids:
                if guid == "entity-2":
                    result[guid] = entity_2
                elif guid == "entity-3":
                    result[guid] = entity_3
                elif guid == "entity-4":
                    result[guid] = entity_4
                elif guid == "entity-5":
                    result[guid] = entity_5
            return result
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity_1)
        
        assert len(result) == 5
        assert all(f"entity-{i}" in result for i in range(1, 6))
        assert result["entity-1"] == entity_1
        assert result["entity-2"] == entity_2
        assert result["entity-3"] == entity_3
        assert result["entity-4"] == entity_4
        assert result["entity-5"] == entity_5
        
        # Verify get_entities_by_guids was called twice
        assert mock_get_entities.call_count == 2


@pytest.mark.asyncio
async def test__get_all_connected_entities_duplicate_references_in_single_entity():
    """Test with an entity that has duplicate references to the same entity."""
    entity = Entity(guid="entity-1")
    referenced_entity = Entity(guid="entity-2")
    
    # Simulate duplicate references (shouldn't happen but good to test)
    with patch.object(entity, 'get_referred_entities', return_value=["entity-2", "entity-2"]), \
         patch("m4i_atlas_core.functions.atlas.get_all_connected_enteties.get_entities_by_guids", new_callable=AsyncMock) as mock_get_entities, \
         patch.object(referenced_entity, 'get_referred_entities', return_value=[]):
        
        # Return entity based on input guids
        def get_entities_side_effect(guids):
            if "entity-2" in guids:
                return {"entity-2": referenced_entity}
            return {}
        
        mock_get_entities.side_effect = get_entities_side_effect
        
        result = await get_all_connected_entities(entity)
        
        # Should only have 2 entities despite duplicate reference
        assert len(result) == 2
        assert "entity-1" in result
        assert "entity-2" in result
        
        # Verify the function handles duplicates by checking guids passed
        mock_get_entities.assert_called_once()
        call_args = mock_get_entities.call_args
        assert "entity-2" in call_args.kwargs['guids']


@pytest.mark.asyncio
async def test__get_all_connected_entities_self_reference():
    """Test with an entity that references itself."""
    entity = Entity(guid="entity-1")
    
    # Entity references itself
    with patch.object(entity, 'get_referred_entities', return_value=["entity-1"]):
        result = await get_all_connected_entities(entity)
        
        # Should only have the single entity and not loop infinitely
        assert len(result) == 1
        assert "entity-1" in result
        assert result["entity-1"] == entity