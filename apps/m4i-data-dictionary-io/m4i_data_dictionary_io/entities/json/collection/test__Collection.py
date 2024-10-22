import pytest

from ..exceptions import QualifiedNameNotValidException
from .Collection import Collection


def test__create_collection_from_dict():
    """
    Tests whether or not a `Collection` can be created from a dict with its attributes
    """

    collection = {
        "system": "system",
        "definition": "definition",
        "name": "collection",
        "qualifiedName": "system--collection",
        "source": "source"
    }

    instance = Collection.from_dict(collection)

    assert instance.system == "system"
    assert instance.definition == "definition"
    assert instance.name == "collection"
    assert instance.qualified_name == "system--collection"
    assert instance.source == "source"
# END test__create_collection_from_dict


def test__create_collection_from_json():
    """
    Tests whether or not a `collection` can be created from a json string with its attributes
    """

    collection = (
        """
        {
            "system": "system",
            "definition": "definition",
            "name": "collection",
            "qualifiedName": "system--collection",
            "source":"source"
        }
        """
    )

    instance = Collection.from_json(collection)

    assert instance.system == "system"
    assert instance.definition == "definition"
    assert instance.name == "collection"
    assert instance.qualified_name == "system--collection"
    assert instance.source == "source"
# END test__create_collection_from_json


def test__collection_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    collection = {
        "system": "system",
        "name": "collection",
        "qualifiedName": "system--collection"
    }

    instance = Collection.from_dict(collection)

    assert instance._qualified_name() == "system--collection"
# END test__collection_calculates_correct_qualified_name


def test__create_collection_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    collection = {
        "system": "system",
        "name": "collection",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        Collection.from_dict(collection)
    # END WITH
# END test__create_collection_with_wrong_qualified_name


def test__collection_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    collection = {
        "system": "system",
        "definition": "definition",
        "name": "collection",
        "qualifiedName": "system--collection",
        "source": "source"
    }

    instance = Collection.from_dict(collection)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.qualified_name == instance.qualified_name

    atlas_system = atlas_attributes.systems[0]

    assert atlas_system is not None
    assert atlas_system.type_name == "m4i_system"
    assert getattr(atlas_system.unique_attributes,
                   "qualified_name") == instance.system

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source
# END test__collection_convert_to_atlas_entity
