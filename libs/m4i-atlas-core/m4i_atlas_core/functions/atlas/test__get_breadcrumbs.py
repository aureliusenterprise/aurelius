from unittest.mock import AsyncMock, patch

import pytest

from ...entities import Entity
from ...entities.atlas.core import ObjectId, Attributes
from .get_breadcrumbs import (
    get_breadcrumbs,
    get_breadcrumbs_for_all_descendants,
    MultipleParentsError
)


def make_object_ids(guids: list[str]) -> list[ObjectId]:
    """Helper to create ObjectId objects from GUIDs."""
    return [
        ObjectId(type_name="test_entity", guid=guid, unique_attributes=Attributes())
        for guid in guids
    ]


# Tests for get_breadcrumbs

@pytest.mark.asyncio
async def test__get_breadcrumbs_single_entity_no_parents():
    """Test breadcrumbs for a single entity with no parents."""
    entity = Entity(guid="entity-1")
    
    with patch.object(entity, 'get_parents', return_value=[]):
        breadcrumbs = await get_breadcrumbs(entity)
        
        assert len(breadcrumbs) == 1
        assert breadcrumbs[0].guid == "entity-1"
        assert breadcrumbs[0] == entity


@pytest.mark.asyncio
async def test__get_breadcrumbs_simple_hierarchy():
    """Test breadcrumbs for a simple linear hierarchy (root -> parent -> child)."""
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(root, 'get_parents', return_value=[]), \
         patch.object(parent, 'get_parents', return_value=make_object_ids(["root-guid"])), \
         patch.object(child, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_entity_by_guid", new_callable=AsyncMock) as mock_get:
        
        def get_entity_side_effect(guid, **kwargs):
            if guid == "root-guid":
                return root
            elif guid == "parent-guid":
                return parent
            return None
        
        mock_get.side_effect = get_entity_side_effect
        
        breadcrumbs = await get_breadcrumbs(child)
        
        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].guid == "root-guid"
        assert breadcrumbs[1].guid == "parent-guid"
        assert breadcrumbs[2].guid == "child-guid"
        assert breadcrumbs[0] == root
        assert breadcrumbs[1] == parent
        assert breadcrumbs[2] == child


@pytest.mark.asyncio
async def test__get_breadcrumbs_multiple_parents_raises_error():
    """Test that multiple parents raise MultipleParentsError when choose_first_parent=False."""
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(child, 'get_parents', return_value=make_object_ids(["parent1-guid", "parent2-guid"])):
        with pytest.raises(MultipleParentsError) as exc_info:
            await get_breadcrumbs(child, choose_first_parent=False)
        
        assert "multiple parents" in str(exc_info.value).lower()
        assert "child-guid" in str(exc_info.value)


@pytest.mark.asyncio
async def test__get_breadcrumbs_multiple_parents_choose_first():
    """Test that multiple parents work when choose_first_parent=True."""
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(child, 'get_parents', return_value=make_object_ids(["parent1-guid", "parent2-guid"])), \
         patch.object(parent1, 'get_parents', return_value=[]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_entity_by_guid", new_callable=AsyncMock) as mock_get:
        
        def get_entity_side_effect(guid, **kwargs):
            if guid == "parent1-guid":
                return parent1
            elif guid == "parent2-guid":
                return parent2
            return None
        
        mock_get.side_effect = get_entity_side_effect
        
        breadcrumbs = await get_breadcrumbs(child, choose_first_parent=True)
        
        assert len(breadcrumbs) == 2
        assert breadcrumbs[0].guid == "parent1-guid"
        assert breadcrumbs[1].guid == "child-guid"
        
        # Verify only the first parent was fetched
        mock_get.assert_called_once_with(guid="parent1-guid", entity_type=Entity, access_token=None)


@pytest.mark.asyncio
async def test__get_breadcrumbs_with_access_token():
    """Test that access token is passed to get_entity_by_guid."""
    parent = Entity(guid="parent-guid")
    child = Entity(guid="child-guid")
    access_token = "test-token-123"
    
    with patch.object(child, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch.object(parent, 'get_parents', return_value=[]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_entity_by_guid", new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = parent
        
        await get_breadcrumbs(child, access_token=access_token)
        
        mock_get.assert_called_once_with(guid="parent-guid", entity_type=Entity, access_token=access_token)


@pytest.mark.asyncio
async def test__get_breadcrumbs_deep_hierarchy():
    """Test breadcrumbs for a deep hierarchy with multiple levels."""
    entity_1 = Entity(guid="entity-1")
    entity_2 = Entity(guid="entity-2")
    entity_3 = Entity(guid="entity-3")
    entity_4 = Entity(guid="entity-4")
    
    # Chain: entity-1 <- entity-2 <- entity-3 <- entity-4
    with patch.object(entity_1, 'get_parents', return_value=[]), \
         patch.object(entity_2, 'get_parents', return_value=make_object_ids(["entity-1"])), \
         patch.object(entity_3, 'get_parents', return_value=make_object_ids(["entity-2"])), \
         patch.object(entity_4, 'get_parents', return_value=make_object_ids(["entity-3"])), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_entity_by_guid", new_callable=AsyncMock) as mock_get:
        
        def get_entity_side_effect(guid, **kwargs):
            entities = {
                "entity-1": entity_1,
                "entity-2": entity_2,
                "entity-3": entity_3,
                "entity-4": entity_4
            }
            return entities.get(guid)
        
        mock_get.side_effect = get_entity_side_effect
        
        breadcrumbs = await get_breadcrumbs(entity_4)
        
        assert len(breadcrumbs) == 4
        assert breadcrumbs[0].guid == "entity-1"
        assert breadcrumbs[1].guid == "entity-2"
        assert breadcrumbs[2].guid == "entity-3"
        assert breadcrumbs[3].guid == "entity-4"


# Tests for get_breadcrumbs_for_all_descendants

@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_single_entity():
    """Test breadcrumbs for a single entity with no descendants."""
    entity = Entity(guid="entity-1")
    
    with patch.object(entity, 'get_parents', return_value=[]), \
         patch.object(entity, 'get_children', return_value=[]), \
         patch.object(entity, 'get_referred_entities', return_value=[]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {"entity-1": entity}
        
        result = await get_breadcrumbs_for_all_descendants(entity)
        
        assert len(result) == 1
        assert "entity-1" in result
        assert len(result["entity-1"]) == 1
        assert result["entity-1"][0].guid == "entity-1"


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_simple_hierarchy():
    """Test breadcrumbs for all descendants in a simple hierarchy."""
    root = Entity(guid="root-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(root, 'get_parents', return_value=[]), \
         patch.object(root, 'get_children', return_value=make_object_ids(["child-guid"])), \
         patch.object(root, 'get_referred_entities', return_value=["child-guid"]), \
         patch.object(child, 'get_parents', return_value=make_object_ids(["root-guid"])), \
         patch.object(child, 'get_children', return_value=[]), \
         patch.object(child, 'get_referred_entities', return_value=["root-guid"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {
            "root-guid": root,
            "child-guid": child
        }
        
        result = await get_breadcrumbs_for_all_descendants(root)
        
        assert len(result) == 2
        
        # Check root breadcrumb
        assert len(result["root-guid"]) == 1
        assert result["root-guid"][0].guid == "root-guid"
        
        # Check child breadcrumb
        assert len(result["child-guid"]) == 2
        assert result["child-guid"][0].guid == "root-guid"
        assert result["child-guid"][1].guid == "child-guid"


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_complex_hierarchy():
    """Test breadcrumbs for all descendants in a complex hierarchy with multiple children."""
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child1 = Entity(guid="child1-guid")
    child2 = Entity(guid="child2-guid")
    
    # Structure: root -> parent -> [child1, child2]
    with patch.object(root, 'get_parents', return_value=[]), \
         patch.object(root, 'get_children', return_value=make_object_ids(["parent-guid"])), \
         patch.object(root, 'get_referred_entities', return_value=["parent-guid"]), \
         patch.object(parent, 'get_parents', return_value=make_object_ids(["root-guid"])), \
         patch.object(parent, 'get_children', return_value=make_object_ids(["child1-guid", "child2-guid"])), \
         patch.object(parent, 'get_referred_entities', return_value=["root-guid", "child1-guid", "child2-guid"]), \
         patch.object(child1, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch.object(child1, 'get_children', return_value=[]), \
         patch.object(child1, 'get_referred_entities', return_value=["parent-guid"]), \
         patch.object(child2, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch.object(child2, 'get_children', return_value=[]), \
         patch.object(child2, 'get_referred_entities', return_value=["parent-guid"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {
            "root-guid": root,
            "parent-guid": parent,
            "child1-guid": child1,
            "child2-guid": child2
        }
        
        result = await get_breadcrumbs_for_all_descendants(root)
        
        assert len(result) == 4
        
        # Check root breadcrumb
        assert len(result["root-guid"]) == 1
        assert result["root-guid"][0].guid == "root-guid"
        
        # Check parent breadcrumb
        assert len(result["parent-guid"]) == 2
        assert result["parent-guid"][0].guid == "root-guid"
        assert result["parent-guid"][1].guid == "parent-guid"
        
        # Check both children breadcrumbs
        assert len(result["child1-guid"]) == 3
        assert result["child1-guid"][0].guid == "root-guid"
        assert result["child1-guid"][1].guid == "parent-guid"
        assert result["child1-guid"][2].guid == "child1-guid"
        
        assert len(result["child2-guid"]) == 3
        assert result["child2-guid"][0].guid == "root-guid"
        assert result["child2-guid"][1].guid == "parent-guid"
        assert result["child2-guid"][2].guid == "child2-guid"


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_multiple_parents_raises_error():
    """Test that multiple parents raise MultipleParentsError in descendants."""
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(parent1, 'get_parents', return_value=[]), \
         patch.object(parent1, 'get_children', return_value=make_object_ids(["child-guid"])), \
         patch.object(parent1, 'get_referred_entities', return_value=["child-guid"]), \
         patch.object(parent2, 'get_parents', return_value=[]), \
         patch.object(parent2, 'get_children', return_value=make_object_ids(["child-guid"])), \
         patch.object(parent2, 'get_referred_entities', return_value=["child-guid"]), \
         patch.object(child, 'get_parents', return_value=make_object_ids(["parent1-guid", "parent2-guid"])), \
         patch.object(child, 'get_children', return_value=[]), \
         patch.object(child, 'get_referred_entities', return_value=["parent1-guid", "parent2-guid"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {
            "parent1-guid": parent1,
            "parent2-guid": parent2,
            "child-guid": child
        }
        
        with pytest.raises(MultipleParentsError):
            await get_breadcrumbs_for_all_descendants(parent1, choose_first_parent=False)


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_multiple_parents_choose_first():
    """Test that multiple parents work with choose_first_parent=True in descendants."""
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")
    
    with patch.object(parent1, 'get_parents', return_value=[]), \
         patch.object(parent1, 'get_children', return_value=make_object_ids(["child-guid"])), \
         patch.object(parent1, 'get_referred_entities', return_value=["child-guid"]), \
         patch.object(parent2, 'get_parents', return_value=[]), \
         patch.object(parent2, 'get_children', return_value=make_object_ids(["child-guid"])), \
         patch.object(parent2, 'get_referred_entities', return_value=["child-guid"]), \
         patch.object(child, 'get_parents', return_value=make_object_ids(["parent1-guid", "parent2-guid"])), \
         patch.object(child, 'get_children', return_value=[]), \
         patch.object(child, 'get_referred_entities', return_value=["parent1-guid", "parent2-guid"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {
            "parent1-guid": parent1,
            "parent2-guid": parent2,
            "child-guid": child
        }
        
        result = await get_breadcrumbs_for_all_descendants(parent1, choose_first_parent=True)
        
        # Should successfully compute breadcrumbs with first parent
        assert "child-guid" in result
        assert len(result["child-guid"]) == 2
        assert result["child-guid"][0].guid == "parent1-guid"
        assert result["child-guid"][1].guid == "child-guid"


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_reuses_parent_breadcrumbs():
    """Test that parent breadcrumbs are efficiently reused (same object references)."""
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child1 = Entity(guid="child1-guid")
    child2 = Entity(guid="child2-guid")
    
    with patch.object(root, 'get_parents', return_value=[]), \
         patch.object(root, 'get_children', return_value=make_object_ids(["parent-guid"])), \
         patch.object(root, 'get_referred_entities', return_value=["parent-guid"]), \
         patch.object(parent, 'get_parents', return_value=make_object_ids(["root-guid"])), \
         patch.object(parent, 'get_children', return_value=make_object_ids(["child1-guid", "child2-guid"])), \
         patch.object(parent, 'get_referred_entities', return_value=["root-guid", "child1-guid", "child2-guid"]), \
         patch.object(child1, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch.object(child1, 'get_children', return_value=[]), \
         patch.object(child1, 'get_referred_entities', return_value=["parent-guid"]), \
         patch.object(child2, 'get_parents', return_value=make_object_ids(["parent-guid"])), \
         patch.object(child2, 'get_children', return_value=[]), \
         patch.object(child2, 'get_referred_entities', return_value=["parent-guid"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {
            "root-guid": root,
            "parent-guid": parent,
            "child1-guid": child1,
            "child2-guid": child2
        }
        
        result = await get_breadcrumbs_for_all_descendants(root)
        
        # Verify parent breadcrumbs are reused (same Entity object references)
        assert result["child1-guid"][0] is result["parent-guid"][0]  # Same root object
        assert result["child1-guid"][1] is result["parent-guid"][1]  # Same parent object
        assert result["child2-guid"][0] is result["parent-guid"][0]  # Same root object
        assert result["child2-guid"][1] is result["parent-guid"][1]  # Same parent object


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_with_access_token():
    """Test that access token is passed through correctly."""
    entity = Entity(guid="entity-1")
    access_token = "test-token-456"
    
    with patch.object(entity, 'get_parents', return_value=[]), \
         patch.object(entity, 'get_children', return_value=[]), \
         patch.object(entity, 'get_referred_entities', return_value=[]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = {"entity-1": entity}
        
        result = await get_breadcrumbs_for_all_descendants(entity, access_token=access_token)
        
        assert len(result) == 1
        mock_get_all.assert_called_once_with(entity)


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_deep_hierarchy():
    """Test breadcrumbs computation for a deep hierarchy with many levels."""
    entities = {}
    for i in range(1, 6):
        guid = f"entity-{i}"
        entity = Entity(guid=guid)
        entities[guid] = entity
    
    # Chain: entity-1 -> entity-2 -> entity-3 -> entity-4 -> entity-5
    with patch.object(entities["entity-1"], 'get_parents', return_value=[]), \
         patch.object(entities["entity-1"], 'get_children', return_value=make_object_ids(["entity-2"])), \
         patch.object(entities["entity-1"], 'get_referred_entities', return_value=["entity-2"]), \
         patch.object(entities["entity-2"], 'get_parents', return_value=make_object_ids(["entity-1"])), \
         patch.object(entities["entity-2"], 'get_children', return_value=make_object_ids(["entity-3"])), \
         patch.object(entities["entity-2"], 'get_referred_entities', return_value=["entity-1", "entity-3"]), \
         patch.object(entities["entity-3"], 'get_parents', return_value=make_object_ids(["entity-2"])), \
         patch.object(entities["entity-3"], 'get_children', return_value=make_object_ids(["entity-4"])), \
         patch.object(entities["entity-3"], 'get_referred_entities', return_value=["entity-2", "entity-4"]), \
         patch.object(entities["entity-4"], 'get_parents', return_value=make_object_ids(["entity-3"])), \
         patch.object(entities["entity-4"], 'get_children', return_value=make_object_ids(["entity-5"])), \
         patch.object(entities["entity-4"], 'get_referred_entities', return_value=["entity-3", "entity-5"]), \
         patch.object(entities["entity-5"], 'get_parents', return_value=make_object_ids(["entity-4"])), \
         patch.object(entities["entity-5"], 'get_children', return_value=[]), \
         patch.object(entities["entity-5"], 'get_referred_entities', return_value=["entity-4"]), \
         patch("m4i_atlas_core.functions.atlas.get_breadcrumbs.get_all_connected_entities", new_callable=AsyncMock) as mock_get_all:
        
        mock_get_all.return_value = entities
        
        result = await get_breadcrumbs_for_all_descendants(entities["entity-1"])
        
        assert len(result) == 5
        
        # Check that each level has correct breadcrumb length
        for i in range(1, 6):
            guid = f"entity-{i}"
            assert len(result[guid]) == i
            # Verify the chain
            for j in range(i):
                assert result[guid][j].guid == f"entity-{j+1}"
