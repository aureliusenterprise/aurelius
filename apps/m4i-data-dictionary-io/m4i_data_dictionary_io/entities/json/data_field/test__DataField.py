import pytest

from ..exceptions import QualifiedNameNotValidException
from .DataField import DataField


def test__create_data_field_from_dict():
    """
    Tests whether or not a `DataField` can be created from a dict with its attributes
    """

    data_field = {
        "attribute": "data-domain--data-entity--data-attribute",
        "dataset": "system--collection--dataset",
        "name": "data field",
        "qualifiedName": "system--collection--dataset--data-field",
        "definition": "definition",
        "field_type": "field_type",
        "source": "source"
    }

    instance = DataField.from_dict(data_field)

    assert instance.attribute == "data-domain--data-entity--data-attribute"
    assert instance.dataset == "system--collection--dataset"
    assert instance.name == "data field"
    assert instance.qualified_name == "system--collection--dataset--data-field"
    assert instance.definition == "definition"
    assert instance.field_type == "field_type"
    assert instance.source == "source"
# END test__create_data_field_from_dict


def test__create_data_field_from_json():
    """
    Tests whether or not a `DataField` can be created from a json string with its attributes
    """

    data_field = (
        """
        {
            "attribute": "data-domain--data-entity--data-attribute",
            "dataset": "system--collection--dataset",
            "name": "data field",
            "qualifiedName": "system--collection--dataset--data-field",
            "definition": "definition",
            "field_type": "field_type",
            "source": "source"
        }
        """
    )

    instance = DataField.from_json(data_field)

    assert instance.attribute == "data-domain--data-entity--data-attribute"
    assert instance.dataset == "system--collection--dataset"
    assert instance.name == "data field"
    assert instance.qualified_name == "system--collection--dataset--data-field"
    assert instance.definition == "definition"
    assert instance.field_type == "field_type"
    assert instance.source == "source"
# END test__create_data_field_from_json


def test__data_field_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    data_field = {
        "attribute": "data-domain--data-entity--data-attribute",
        "dataset": "system--collection--dataset",
        "name": "data field",
        "qualifiedName": "system--collection--dataset--data-field"
    }

    instance = DataField.from_dict(data_field)

    assert instance._qualified_name() == "system--collection--dataset--data-field"
# END test__data_field_calculates_correct_qualified_name


def test__create_data_field_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    data_field = {
        "attribute": "data-domain--data-entity--data-attribute",
        "dataset": "system--collection--dataset",
        "name": "data field",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        DataField.from_dict(data_field)
    # END WITH
# END test__create_data_field_with_wrong_qualified_name


def test__data_field_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    data_field = {
        "attribute": "data-domain--data-entity--data-attribute",
        "dataset": "system--collection--dataset",
        "name": "data field",
        "qualifiedName": "system--collection--dataset--data-field",
        "definition": "definition",
        "field_type": "field_type",
        "source": "source"
    }

    instance = DataField.from_dict(data_field)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.field_type == instance.field_type
    assert atlas_attributes.qualified_name == instance.qualified_name

    atlas_data_attribute = atlas_attributes.attributes[0]

    assert atlas_data_attribute is not None
    assert atlas_data_attribute.type_name == "m4i_data_attribute"
    assert getattr(atlas_data_attribute.unique_attributes,
                   "qualified_name") == instance.attribute

    atlas_dataset = atlas_attributes.datasets[0]

    assert atlas_dataset is not None
    assert atlas_dataset.type_name == "m4i_dataset"
    assert getattr(atlas_dataset.unique_attributes,
                   "qualified_name") == instance.dataset

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source

# END test__data_field_convert_to_atlas_entity
