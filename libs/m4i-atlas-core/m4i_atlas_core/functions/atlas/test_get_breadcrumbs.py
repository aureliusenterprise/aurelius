from typing import Dict, List
from unittest.mock import AsyncMock, call, patch
import sys

import pytest

# Import the module itself to ensure it's in sys.modules
from . import get_breadcrumbs as get_breadcrumbs_module

from ...entities import Entity
from ...entities.atlas.core import Attributes, ObjectId
from .get_breadcrumbs import MultipleParentsError, get_breadcrumbs, get_breadcrumbs_for_all_descendants


def make_object_ids(guids: List[str]) -> List[ObjectId]:
    return [
        ObjectId(type_name="test_entity", guid=guid, unique_attributes=Attributes())
        for guid in guids
    ]


@pytest.mark.asyncio
async def test__get_breadcrumbs_single_entity_no_parents():
    entity = Entity(guid="entity-1")

    with patch.object(entity, "get_parents", return_value=[]):
        breadcrumbs = await get_breadcrumbs(entity)
        assert breadcrumbs == []


@pytest.mark.asyncio
async def test__get_breadcrumbs_simple_hierarchy():
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child = Entity(guid="child-guid")

    def get_entity_side_effect(*, guid: str, **_kwargs):
        return {"root-guid": root, "parent-guid": parent}[guid]

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(root, "get_parents", return_value=[]), \
        patch.object(parent, "get_parents", return_value=make_object_ids(["root-guid"])), \
        patch.object(child, "get_parents", return_value=make_object_ids(["parent-guid"])), \
        patch.object(gb_module, "get_entity_by_guid", new=AsyncMock()) as mock_get_entity:
        mock_get_entity.side_effect = get_entity_side_effect

        breadcrumbs = await get_breadcrumbs(child)

        assert [e.guid for e in breadcrumbs] == ["root-guid", "parent-guid"]
        mock_get_entity.assert_has_calls(
            [
                call(guid="parent-guid", entity_type=Entity, access_token=None),
                call(guid="root-guid", entity_type=Entity, access_token=None),
            ]
        )


@pytest.mark.asyncio
async def test__get_breadcrumbs_multiple_parents_raises_error():
    child = Entity(guid="child-guid")
    with patch.object(
        child,
        "get_parents",
        return_value=make_object_ids(["parent1-guid", "parent2-guid"]),
    ):
        with pytest.raises(MultipleParentsError) as exc_info:
            await get_breadcrumbs(child, choose_first_parent=False)
        assert "multiple parents" in str(exc_info.value).lower()
        assert "child-guid" in str(exc_info.value)


@pytest.mark.asyncio
async def test__get_breadcrumbs_multiple_parents_choose_first():
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")

    def get_entity_side_effect(*, guid: str, **_kwargs):
        return {"parent1-guid": parent1, "parent2-guid": parent2}[guid]

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(
        child,
        "get_parents",
        return_value=make_object_ids(["parent1-guid", "parent2-guid"]),
    ), patch.object(parent1, "get_parents", return_value=[]), patch.object(
        gb_module, "get_entity_by_guid", new=AsyncMock()
    ) as mock_get_entity:
        mock_get_entity.side_effect = get_entity_side_effect

        breadcrumbs = await get_breadcrumbs(child, choose_first_parent=True)
        assert [e.guid for e in breadcrumbs] == ["parent1-guid"]
        mock_get_entity.assert_called_once_with(
            guid="parent1-guid", entity_type=Entity, access_token=None
        )


@pytest.mark.asyncio
async def test__get_breadcrumbs_with_access_token():
    parent = Entity(guid="parent-guid")
    child = Entity(guid="child-guid")
    access_token = "test-token-123"

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(child, "get_parents", return_value=make_object_ids(["parent-guid"])), \
        patch.object(parent, "get_parents", return_value=[]), \
        patch.object(gb_module, "get_entity_by_guid", new=AsyncMock()) as mock_get_entity:
        mock_get_entity.return_value = parent

        await get_breadcrumbs(child, access_token=access_token)
        mock_get_entity.assert_called_once_with(
            guid="parent-guid", entity_type=Entity, access_token=access_token
        )


@pytest.mark.asyncio
async def test__get_breadcrumbs_deep_hierarchy():
    entity_1 = Entity(guid="entity-1")
    entity_2 = Entity(guid="entity-2")
    entity_3 = Entity(guid="entity-3")
    entity_4 = Entity(guid="entity-4")

    def get_entity_side_effect(*, guid: str, **_kwargs):
        return {
            "entity-1": entity_1,
            "entity-2": entity_2,
            "entity-3": entity_3,
        }[guid]

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(entity_1, "get_parents", return_value=[]), \
        patch.object(entity_2, "get_parents", return_value=make_object_ids(["entity-1"])), \
        patch.object(entity_3, "get_parents", return_value=make_object_ids(["entity-2"])), \
        patch.object(entity_4, "get_parents", return_value=make_object_ids(["entity-3"])), \
        patch.object(gb_module, "get_entity_by_guid", new=AsyncMock()) as mock_get_entity:
        mock_get_entity.side_effect = get_entity_side_effect

        breadcrumbs = await get_breadcrumbs(entity_4)
        assert [e.guid for e in breadcrumbs] == ["entity-1", "entity-2", "entity-3"]


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_single_entity():
    entity = Entity(guid="entity-1")

    all_entities: Dict[str, Entity] = {"entity-1": entity}

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(entity, "get_parents", return_value=[]), patch.object(
        gb_module, "get_all_connected_entities", new=AsyncMock()
    ) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(entity)
        assert list(result.keys()) == ["entity-1"]
        assert result["entity-1"] == []
        mock_get_all.assert_called_once_with(entity, access_token=None)


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_simple_hierarchy():
    root = Entity(guid="root-guid")
    child = Entity(guid="child-guid")

    all_entities: Dict[str, Entity] = {"root-guid": root, "child-guid": child}

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(root, "get_parents", return_value=[]), patch.object(
        child, "get_parents", return_value=make_object_ids(["root-guid"])
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(root)
        assert [e.guid for e in result["root-guid"]] == []
        assert [e.guid for e in result["child-guid"]] == ["root-guid"]


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_complex_hierarchy():
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child1 = Entity(guid="child1-guid")
    child2 = Entity(guid="child2-guid")

    all_entities: Dict[str, Entity] = {
        "root-guid": root,
        "parent-guid": parent,
        "child1-guid": child1,
        "child2-guid": child2,
    }

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(root, "get_parents", return_value=[]), patch.object(
        parent, "get_parents", return_value=make_object_ids(["root-guid"])
    ), patch.object(
        child1, "get_parents", return_value=make_object_ids(["parent-guid"])
    ), patch.object(
        child2, "get_parents", return_value=make_object_ids(["parent-guid"])
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(root)
        assert [e.guid for e in result["root-guid"]] == []
        assert [e.guid for e in result["parent-guid"]] == ["root-guid"]
        assert [e.guid for e in result["child1-guid"]] == ["root-guid", "parent-guid"]
        assert [e.guid for e in result["child2-guid"]] == ["root-guid", "parent-guid"]


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_multiple_parents_raises_error():
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")

    all_entities: Dict[str, Entity] = {
        "parent1-guid": parent1,
        "parent2-guid": parent2,
        "child-guid": child,
    }

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(parent1, "get_parents", return_value=[]), patch.object(
        parent2, "get_parents", return_value=[]
    ), patch.object(
        child,
        "get_parents",
        return_value=make_object_ids(["parent1-guid", "parent2-guid"]),
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = all_entities

        with pytest.raises(MultipleParentsError):
            await get_breadcrumbs_for_all_descendants(parent1, choose_first_parent=False)


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_multiple_parents_choose_first():
    parent1 = Entity(guid="parent1-guid")
    parent2 = Entity(guid="parent2-guid")
    child = Entity(guid="child-guid")

    all_entities: Dict[str, Entity] = {
        "parent1-guid": parent1,
        "parent2-guid": parent2,
        "child-guid": child,
    }

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(parent1, "get_parents", return_value=[]), patch.object(
        parent2, "get_parents", return_value=[]
    ), patch.object(
        child,
        "get_parents",
        return_value=make_object_ids(["parent1-guid", "parent2-guid"]),
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(parent1, choose_first_parent=True)
        assert [e.guid for e in result["child-guid"]] == ["parent1-guid"]


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_reuses_parent_breadcrumbs():
    root = Entity(guid="root-guid")
    parent = Entity(guid="parent-guid")
    child1 = Entity(guid="child1-guid")
    child2 = Entity(guid="child2-guid")

    all_entities: Dict[str, Entity] = {
        "root-guid": root,
        "parent-guid": parent,
        "child1-guid": child1,
        "child2-guid": child2,
    }

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(root, "get_parents", return_value=[]), patch.object(
        parent, "get_parents", return_value=make_object_ids(["root-guid"])
    ), patch.object(
        child1, "get_parents", return_value=make_object_ids(["parent-guid"])
    ), patch.object(
        child2, "get_parents", return_value=make_object_ids(["parent-guid"])
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(root)
        assert result["child1-guid"][0] is result["parent-guid"][0]
        assert result["child2-guid"][0] is result["parent-guid"][0]


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_with_access_token():
    entity = Entity(guid="entity-1")
    access_token = "test-token-456"

    all_entities: Dict[str, Entity] = {"entity-1": entity}

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(entity, "get_parents", return_value=[]), patch.object(
        gb_module, "get_all_connected_entities", new=AsyncMock()
    ) as mock_get_all:
        mock_get_all.return_value = all_entities

        result = await get_breadcrumbs_for_all_descendants(entity, access_token=access_token)
        assert list(result.keys()) == ["entity-1"]
        mock_get_all.assert_called_once_with(entity, access_token=access_token)


@pytest.mark.asyncio
async def test__get_breadcrumbs_for_all_descendants_deep_hierarchy():
    entities: Dict[str, Entity] = {}
    for i in range(1, 6):
        guid = f"entity-{i}"
        entities[guid] = Entity(guid=guid)

    # Get the actual module from sys.modules
    gb_module = sys.modules['m4i_atlas_core.functions.atlas.get_breadcrumbs']
    
    with patch.object(entities["entity-1"], "get_parents", return_value=[]), patch.object(
        entities["entity-2"], "get_parents", return_value=make_object_ids(["entity-1"])
    ), patch.object(
        entities["entity-3"], "get_parents", return_value=make_object_ids(["entity-2"])
    ), patch.object(
        entities["entity-4"], "get_parents", return_value=make_object_ids(["entity-3"])
    ), patch.object(
        entities["entity-5"], "get_parents", return_value=make_object_ids(["entity-4"])
    ), patch.object(gb_module, "get_all_connected_entities", new=AsyncMock()) as mock_get_all:
        mock_get_all.return_value = entities

        result = await get_breadcrumbs_for_all_descendants(entities["entity-1"])

        # Breadcrumbs are ancestors only: length = i-1
        for i in range(1, 6):
            guid = f"entity-{i}"
            assert len(result[guid]) == i - 1
            for j in range(i - 1):
                assert result[guid][j].guid == f"entity-{j+1}"
