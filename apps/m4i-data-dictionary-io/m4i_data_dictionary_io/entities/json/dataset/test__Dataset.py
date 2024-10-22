import pytest

from ..exceptions import QualifiedNameNotValidException
from .Dataset import Dataset


def test__create_dataset_from_dict():
    """
    Tests whether or not a `Dataset` can be created from a dict with its attributes
    """

    dataset = {
        "collection": "system--collection",
        "definition": "definition",
        "name": "dataset",
        "source": "source",
        "qualifiedName": "system--collection--dataset"
    }

    instance = Dataset.from_dict(dataset)

    assert instance.collection == "system--collection"
    assert instance.definition == "definition"
    assert instance.name == "dataset"
    assert instance.qualified_name == "system--collection--dataset"
    assert instance.source == "source"
# END test__create_dataset_from_dict


def test__create_dataset_from_json():
    """
    Tests whether or not a `Dataset` can be created from a json string with its attributes
    """

    dataset = (
        """
        {
            "collection": "system--collection",
            "definition": "definition",
            "name": "dataset",
            "qualifiedName": "system--collection--dataset",
            "source": "source"
        }
        """
    )

    instance = Dataset.from_json(dataset)

    assert instance.collection == "system--collection"
    assert instance.definition == "definition"
    assert instance.name == "dataset"
    assert instance.qualified_name == "system--collection--dataset"
    assert instance.source == "source"
# END test__create_dataset_from_json


def test__dataset_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    dataset = {
        "collection": "system--collection",
        "name": "dataset",
        "qualifiedName": "system--collection--dataset"
    }

    instance = Dataset.from_dict(dataset)

    assert instance._qualified_name() == "system--collection--dataset"
# END test__dataset_calculates_correct_qualified_name


def test__create_dataset_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    dataset = {
        "collection": "system--collection",
        "name": "dataset",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        Dataset.from_dict(dataset)
    # END WITH
# END test__create_dataset_with_wrong_qualified_name


def test__dataset_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    dataset = {
        "collection": "system--collection",
        "definition": "definition",
        "name": "dataset",
        "qualifiedName": "system--collection--dataset",
        "source": "source"
    }

    instance = Dataset.from_dict(dataset)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.qualified_name == instance.qualified_name

    atlas_collection = atlas_attributes.collections[0]

    assert atlas_collection is not None
    assert atlas_collection.type_name == "m4i_collection"
    assert getattr(atlas_collection.unique_attributes,
                   "qualified_name") == instance.collection

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source

# END test__dataset_convert_to_atlas_entity
