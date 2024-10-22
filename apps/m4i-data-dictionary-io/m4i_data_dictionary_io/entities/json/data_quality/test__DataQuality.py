import pytest

from ..exceptions import QualifiedNameNotValidException
from .DataQuality import DataQuality


def test__create_data_quality_from_dict():
    """
    Tests whether or not a `DataQuality` can be created from a dict with its attributes
    """
    data_quality = {
        "id": "1",
        "qualifiedName": "data-field--1",
        "ruleDescription": "Rule Description",
        "expression": "expression('data-field')",
        "active": "1",
        "expressionVersion": "1",
        "businessRuleDescription": "Business Rule",
        "filterRequired": "Yes",
        "qualityDimension": "Quality Dimension",
        "dataField": "data-field",
        "source": "source"
    }

    instance = DataQuality.from_dict(data_quality)

    assert instance.data_field == "data-field"
    assert instance.qualified_name == "data-field--1"
    assert instance.rule_description == "Rule Description"
    assert instance.expression == "expression('data-field')"
    assert instance.active == "1"
    assert instance.expression_version == "1"
    assert instance.business_rule_description == "Business Rule"
    assert instance.filter_required == "Yes"
    assert instance.quality_dimension == "Quality Dimension"
    assert instance.source == "source"

# END test__create_data_quality_from_dict


def test__create_data_quality_from_json():
    """
    Tests whether or not a `DataQuality` can be created from a json string with its attributes
    """

    data_quality = (
        """
        {
            "id": "1",
            "qualifiedName": "data-field--1",
            "ruleDescription": "Rule Description",
            "expression": "expression('data-field')",
            "active": "1",
            "expressionVersion": "1",
            "businessRuleDescription": "Business Rule",
            "filterRequired": "Yes",
            "qualityDimension": "Quality Dimension",
            "dataField": "data-field",
            "source": "source"
        }
        """
    )

    instance = DataQuality.from_json(data_quality)

    assert instance.id == "1"
    assert instance.data_field == "data-field"
    assert instance.qualified_name == "data-field--1"
    assert instance.rule_description == "Rule Description"
    assert instance.expression == "expression('data-field')"
    assert instance.active == "1"
    assert instance.expression_version == "1"
    assert instance.business_rule_description == "Business Rule"
    assert instance.filter_required == "Yes"
    assert instance.quality_dimension == "Quality Dimension"
    assert instance.source == "source"


# END test__create_data_quality_from_json


def test__data_quality_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    data_quality = {
        "id": "1",
        "dataField": "data-field",
        "qualifiedName": "data-field--1"
    }

    instance = DataQuality.from_dict(data_quality)

    assert instance._qualified_name() == "data-field--1"


# END test__data_quality_calculates_correct_qualified_name


def test__create_data_quality_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    data_quality = {
        "dataField": "data-field",
        "id": "1",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        DataQuality.from_dict(data_quality)
    # END WITH


# END test__create_data_quality_with_wrong_qualified_name


def test__data_quality_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    data_quality = {
        "id": "1",
        "dataField": "data-field",
        "qualifiedName": "data-field--1",
        "ruleDescription": "Rule Description",
        "expression": "expression('data-field')",
        "active": "1",
        "expressionVersion": "1",
        "businessRuleDescription": "Business Rule",
        "filterRequired": "Yes",
        "qualityDimension": "Quality Dimension",
        "source": "source"
    }

    instance = DataQuality.from_dict(data_quality)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.id == instance.id
    assert atlas_attributes.rule_description == instance.rule_description
    assert atlas_attributes.expression == instance.expression
    assert atlas_attributes.active == bool(instance.active)
    assert atlas_attributes.expression_version == instance.expression_version
    assert atlas_attributes.business_rule_description == instance.business_rule_description
    assert atlas_attributes.filter_required == bool(instance.filter_required)
    assert atlas_attributes.quality_dimension == instance.quality_dimension
    assert atlas_attributes.qualified_name == instance.qualified_name

    field_entity = atlas_attributes.fields[0]
    assert field_entity is not None
    assert field_entity.type_name == "m4i_field"
    assert getattr(field_entity.unique_attributes,
                   "qualified_name") == instance.data_field

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source


# END test__data_quality_convert_to_atlas_entity





