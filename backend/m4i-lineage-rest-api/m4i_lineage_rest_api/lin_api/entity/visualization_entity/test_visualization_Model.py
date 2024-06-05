import pytest

from .visualization_Model import Visualization


def test__create_visualization_from_dict():
    """
    Tests whether or not a `Visualization` can be created from a dict with its attributes
    """

    visualization = {
        "qualifiedName": "test_m4i_visualization_entity",
        "name": "test_m4i_visualization_entity",
        "description": "something",
        "updatedAt": "Updated At",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ],
        "childDataset": [
            "tester_m4i_indexPattern"
        ],
        "type": "a type",
        "visualizationType": "visualization type"
    }

    instance = Visualization.from_dict(visualization)

    assert instance.name == "test_m4i_visualization_entity"
    assert instance._qualified_name() == "test_m4i_visualization_entity"


# END test__create_visualization_from_dict


def test__visualization_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    visualization = {
        "qualifiedName": "test_m4i_visualization_entity",
        "name": "test_m4i_visualization_entity",
        "description": "something",
        "updatedAt": "Updated At",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ],
        "childDataset": [
            "tester_m4i_indexPattern"
        ],
        "type": "a type",
        "visualizationType": "visualization type"
    }

    instance = Visualization.from_dict(visualization)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.qualified_name == instance._qualified_name()
    assert atlas_attributes.updated_at == instance.updated_at
    assert atlas_attributes.version == instance.version


# END test__visualization_convert_to_atlas_entity

def test__visualization_convert_to_atlas_entity_with_dataset():
    """
    Tests whether or not the `Child Dataset` field is correctly converted to the atlas format.
    """

    visualization = {
        "qualifiedName": "test_m4i_visualization_entity",
        "name": "test_m4i_visualization_entity",
        "description": "something",
        "updatedAt": "Updated At",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ],
        "childDataset": [
            "tester_m4i_indexPattern"
        ],
        "type": "a type",
        "visualizationType": "visualization type"
    }

    instance = Visualization.from_dict(visualization)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_dataset = atlas_attributes.child_dataset

    for dataset in atlas_dataset:
        assert dataset is not None
        assert dataset.type_name == "m4i_index_pattern"
        assert getattr(dataset.unique_attributes,
                       "qualified_name") == instance.child_dataset[0]
# END test__visualization_convert_to_atlas_entity_with_dataset
