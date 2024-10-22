import pytest

from ..exceptions import QualifiedNameNotValidException
from .DataEntity import DataEntity


def test__create_data_entity_from_dict():
    """
    Tests whether or not a `DataEntity` can be created from a dict with its attributes
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--parent-entity--data-entity",
        "businessOwner": "owner",
        "definition": "definition",
        "parentEntity": "data-domain--parent-entity",
        "steward": "steward",
        "source": "source"
    }

    instance = DataEntity.from_dict(data_entity)

    assert instance.data_domain == "data-domain"
    assert instance.name == "data entity"
    assert instance.qualified_name == "data-domain--parent-entity--data-entity"
    assert instance.business_owner == "owner"
    assert instance.definition == "definition"
    assert instance.parent_entity == "data-domain--parent-entity"
    assert instance.steward == "steward"
    assert instance.source == "source"
# END test__create_data_entity_from_dict


def test__create_data_entity_from_json():
    """
    Tests whether or not a `DataEntity` can be created from a json string with its attributes
    """

    data_entity = (
        """
        {
            "dataDomain": "data-domain",
            "name": "data entity",
            "qualifiedName": "data-domain--parent-entity--data-entity",
            "businessOwner": "owner",
            "definition": "definition",
            "parentEntity": "data-domain--parent-entity",
            "steward": "steward",
            "source": "source"
        }
        """
    )

    instance = DataEntity.from_json(data_entity)

    assert instance.data_domain == "data-domain"
    assert instance.name == "data entity"
    assert instance.qualified_name == "data-domain--parent-entity--data-entity"
    assert instance.business_owner == "owner"
    assert instance.definition == "definition"
    assert instance.parent_entity == "data-domain--parent-entity"
    assert instance.steward == "steward"
    assert instance.source == "source"
# END test__create_data_entity_from_json


def test__data_entity_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--data-entity",
    }

    instance = DataEntity.from_dict(data_entity)

    assert instance._qualified_name() == "data-domain--data-entity"
# END test__data_entity_calculates_correct_qualified_name


def test__create_data_entity_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        DataEntity.from_dict(data_entity)
    # END WITH
# END test__create_data_entity_with_wrong_qualified_name


def test__data_entity_with_parent_has_parent():
    """
    Tests whether or not the `has_parent` attribute is `True` whenever a parent entity is set.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--parent-entity--data-entity",
        "parentEntity": "data-domain--parent-entity",
    }

    instance = DataEntity.from_dict(data_entity)

    assert instance.has_parent
# END test__data_entity_with_parent_has_parent


def test__data_entity_without_parent_has_no_parent():
    """
    Tests whether or not the `has_parent` attribute is `False` whenever no parent entity is set.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--data-entity",
    }

    instance = DataEntity.from_dict(data_entity)

    assert not instance.has_parent
# END test__data_entity_without_parent_has_no_parent


def test__data_entity_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--data-entity",
        "definition": "definition",
        "source": "source"
    }

    instance = DataEntity.from_dict(data_entity)

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
# END test__data_entity_convert_to_atlas_entity


def test__data_entity_convert_to_atlas_entity_with_business_owner():
    """
    Tests whether or not the `business_owner` field is correctly converted to the atlas format.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--data-entity",
        "businessOwner": "owner"
    }

    instance = DataEntity.from_dict(data_entity)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_business_owner = atlas_attributes.business_owner[0]

    assert atlas_business_owner is not None
    assert atlas_business_owner.type_name == "m4i_person"
    assert getattr(atlas_business_owner.unique_attributes,
                   "qualified_name") == instance.business_owner
# END test__data_entity_convert_to_atlas_entity_with_business_owner


def test__data_entity_convert_to_atlas_entity_with_data_steward():
    """
    Tests whether or not the `steward` field is correctly converted to the atlas format.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--data-entity",
        "steward": "steward"
    }

    instance = DataEntity.from_dict(data_entity)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_steward = atlas_attributes.steward[0]

    assert atlas_steward is not None
    assert atlas_steward.type_name == "m4i_person"
    assert getattr(atlas_steward.unique_attributes,
                   "qualified_name") == instance.steward
# END test__data_entity_convert_to_atlas_entity_with_data_steward


def test__convert_to_atlas_entity_with_parent_entity():
    """
    Tests whether or not the `parent_entity` field is correctly converted to the atlas format.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--parent-entity--data-entity",
        "parentEntity": "data-domain--parent-entity"
    }

    instance = DataEntity.from_dict(data_entity)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    parent_entity = atlas_attributes.parent_entity[0]

    assert parent_entity is not None
    assert parent_entity.type_name == "m4i_data_entity"
    assert getattr(parent_entity.unique_attributes,
                   "qualified_name") == instance.parent_entity
# END test__data_entity_convert_to_atlas_entity_with_parent_entity

def test__convert_to_atlas_entity_with_parent_entity_and_link_yes():
    """
    Tests whether or not the `parent_entity` field is correctly converted to the atlas format.
    """

    data_entity = {
        "dataDomain": "data-domain",
        "name": "data entity",
        "qualifiedName": "data-domain--parent-entity--data-entity",
        "parentEntity": "data-domain--parent-entity",
        "domainLink": "Yes"
    }

    instance = DataEntity.from_dict(data_entity)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    parent_entity = atlas_attributes.parent_entity[0]

    assert parent_entity is not None
    assert parent_entity.type_name == "m4i_data_entity"
    assert getattr(parent_entity.unique_attributes,
                   "qualified_name") == instance.parent_entity

    domain_entity = atlas_attributes.data_domain[0]
    assert domain_entity is not None
    assert domain_entity.type_name == "m4i_data_domain"
    assert getattr(domain_entity.unique_attributes,
                   "qualified_name") == instance.data_domain
# END test__data_entity_convert_to_atlas_entity_with_parent_entity
