import pytest

from .indexPattern_Model import IndexPattern


def test__create_index_pattern_from_dict():
    """
    Tests whether or not a `IndexPattern` can be created from a dict with its attributes
    """

    index_pattern = {
        "qualifiedName": "test_m4i_indexPattern",
        "name": "test_m4i_indexPattern",
        "description": "something",
        "indexPattern": "pattern",
        "updatedAt": "updated at",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = IndexPattern.from_dict(index_pattern)

    assert instance.name == "test_m4i_indexPattern"
    assert instance._qualified_name() == "test_m4i_indexpattern"


# END test__create_index_pattern_from_dict


def test__create_index_pattern_from_json():
    """
    Tests whether or not a `IndexPattern` can be created from a json string with its attributes
    """

    index_pattern = (
        """
        {
            "qualifiedName": "test_m4i_indexPattern",
            "name": "test_m4i_indexPattern",
            "description": "something",
            "indexPattern": "pattern",
            "updatedAt": "updated at",
            "version": "VERSION",
            "creator": [
                "test_m4i_person"
            ],
            "parentDataset": [
                "tester_m4i_visualization"
            ]
        }
        """
    )

    instance = IndexPattern.from_json(index_pattern)

    assert instance.name == "test_m4i_indexPattern"
    assert instance._qualified_name() == "test_m4i_indexpattern"
    assert instance.description == "something"
    assert instance.version == "VERSION"


# END test__create_index_pattern_from_json


def test__index_pattern_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    index_pattern = {
        "qualifiedName": "test_m4i_indexPattern",
        "name": "test_m4i_indexPattern",
        "description": "something",
        "indexPattern": "pattern",
        "updatedAt": "updated at",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = IndexPattern.from_dict(index_pattern)

    assert instance._qualified_name() == "test_m4i_indexpattern"


# END test__index_pattern_calculates_correct_qualified_name


def test__index_pattern_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    index_pattern = {
        "qualifiedName": "test_m4i_indexPattern",
        "name": "test_m4i_indexPattern",
        "description": "something",
        "indexPattern": "pattern",
        "updatedAt": "updated at",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = IndexPattern.from_dict(index_pattern)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.description == instance.description
    assert atlas_attributes.updated_at == instance.updated_at
    assert atlas_attributes.version == instance.version
    # assert atlas_attributes.creator == instance.creator
    assert atlas_attributes.qualified_name == instance._qualified_name()
    atlas_person = atlas_attributes.creator

    for person in atlas_person:
        assert person is not None
        assert person.type_name == "m4i_person"
        assert getattr(person.unique_attributes,
                       "qualified_name") == instance.creator[0]

# END test__index_pattern_convert_to_atlas_entity
