import pytest
from m4i_atlas_core import ConfigStore

from config import config
from credentials import credentials
from ..exceptions import QualifiedNameNotValidException
from .DataAttribute import DataAttribute


def test__create_data_attribute_from_dict():
    """
    Tests whether or not a `DataAttribute` can be created from a dict with its attributes
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "data-domain--data-entity--data-attribute",
        "businessOwner": "owner",
        "definition": "definition",
        "steward": "steward",
        "source": "source",
        "has_pii": "Yes",
        "is_key_data": "Yes",
        "risk_classification": "Low"
    }

    instance = DataAttribute.from_dict(data_attribute)

    assert instance.data_entity == "data-domain--data-entity"
    assert instance.name == "data attribute"
    assert instance.qualified_name == "data-domain--data-entity--data-attribute"
    assert instance.business_owner == "owner"
    assert instance.definition == "definition"
    assert instance.steward == "steward"
    assert instance.source == "source"
    assert instance.has_pii == "Yes"
    assert instance.is_key_data == "Yes"
    assert instance.risk_classification == "Low"


# END test__create_data_attribute_from_dict


def test__create_data_attribute_from_json():
    """
    Tests whether or not a `DataAttribute` can be created from a json string with its attributes
    """

    data_attribute = (
        """
        {
            "dataEntity": "data-domain--data-entity",
            "name": "data attribute",
            "qualifiedName": "data-domain--data-entity--data-attribute",
            "businessOwner": "owner",
            "definition": "definition",
            "steward": "steward",
            "source": "source",
            "has_pii" : "Yes",
        "is_key_data": "Yes",
        "risk_classification": "Low"
        }
        """
    )

    instance = DataAttribute.from_json(data_attribute)

    assert instance.data_entity == "data-domain--data-entity"
    assert instance.name == "data attribute"
    assert instance.qualified_name == "data-domain--data-entity--data-attribute"
    assert instance.business_owner == "owner"
    assert instance.definition == "definition"
    assert instance.steward == "steward"
    assert instance.source == "source"
    assert instance.has_pii == "Yes"
    assert instance.is_key_data == "Yes"
    assert instance.risk_classification == "Low"


# END test__create_data_attribute_from_json


def test__data_attribute_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "data-domain--data-entity--data-attribute",
    }

    instance = DataAttribute.from_dict(data_attribute)

    assert instance._qualified_name() == "data-domain--data-entity--data-attribute"
# END test__data_attribute_calculates_correct_qualified_name


def test__create_data_attribute_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        DataAttribute.from_dict(data_attribute)
    # END WITH
# END test__create_data_attribute_with_wrong_qualified_name


def test__data_attribute_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "data-domain--data-entity--data-attribute",
        "definition": "definition",
        "source": "source",
        "has_pii": "Yes",
        "is_key_data": "Yes",
        "risk_classification": "Low"
    }

    instance = DataAttribute.from_dict(data_attribute)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.qualified_name == instance.qualified_name

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source

    atlas_classifications = atlas_instance.classifications
    assert len(atlas_classifications)==3
    assert atlas_classifications[0].type_name == 'PII'
    assert atlas_classifications[1].type_name == 'key_data'
    assert atlas_classifications[2].type_name == 'low_risk'

# END test__data_attribute_convert_to_atlas_entity


def test__data_attribute_convert_to_atlas_entity_with_business_owner():
    """
    Tests whether or not the `business_owner` field is correctly converted to the atlas format.
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "data-domain--data-entity--data-attribute",
        "businessOwner": "owner"
    }

    instance = DataAttribute.from_dict(data_attribute)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_business_owner = atlas_attributes.business_owner[0]

    assert atlas_business_owner is not None
    assert atlas_business_owner.type_name == "m4i_person"
    assert getattr(atlas_business_owner.unique_attributes,
                   "qualified_name") == instance.business_owner
# END test__data_attribute_convert_to_atlas_entity_with_business_owner


def test__data_attribute_convert_to_atlas_entity_with_data_steward():
    """
    Tests whether or not the `steward` field is correctly converted to the atlas format.
    """

    data_attribute = {
        "dataEntity": "data-domain--data-entity",
        "name": "data attribute",
        "qualifiedName": "data-domain--data-entity--data-attribute",
        "steward": "steward",
        "attribute_type": "attribute_type",

    }

    instance = DataAttribute.from_dict(data_attribute)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_steward = atlas_attributes.steward[0]

    assert atlas_steward is not None
    assert atlas_steward.type_name == "m4i_person"
    assert getattr(atlas_steward.unique_attributes,
                   "qualified_name") == instance.steward
# END test__data_attribute_convert_to_atlas_entity_with_data_steward
