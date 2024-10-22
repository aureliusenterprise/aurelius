import pytest

from ..exceptions import QualifiedNameNotValidException
from .DataDomain import DataDomain


def test__create_data_domain_from_dict():
    """
    Tests whether or not a `DataDomain` can be created from a dict with its attributes
    """

    data_domain = {
        "name": "data domain",
        "qualifiedName": "data-domain",
        "definition": "definition",
        "domainLead": "domain lead",
        "source": "source"
    }

    instance = DataDomain.from_dict(data_domain)

    assert instance.name == "data domain"
    assert instance.qualified_name == "data-domain"
    assert instance.definition == "definition"
    assert instance.domain_lead == "domain lead"
    assert instance.source == "source"
# END test__create_data_domain_from_dict


def test__create_data_domain_from_json():
    """
    Tests whether or not a `DataDomain` can be created from a json string with its attributes
    """

    data_domain = (
        """
        {
            "name": "data domain",
            "qualifiedName": "data-domain",
            "businessOwner": "owner",
            "definition": "definition",
            "domainLead": "domain lead",
            "source": "source"
        }
        """
    )

    instance = DataDomain.from_json(data_domain)

    assert instance.name == "data domain"
    assert instance.qualified_name == "data-domain"
    assert instance.definition == "definition"
    assert instance.domain_lead == "domain lead"
    assert instance.source == "source"
# END test__create_data_domain_from_json


def test__data_domain_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    data_domain = {
        "name": "data domain",
        "qualifiedName": "data-domain"
    }

    instance = DataDomain.from_dict(data_domain)

    assert instance._qualified_name() == "data-domain"
# END test__data_domain_calculates_correct_qualified_name


def test__create_data_attribute_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    data_domain = {
        "name": "data domain",
        "qualifiedName": "test"
    }

    with pytest.raises(QualifiedNameNotValidException):
        DataDomain.from_dict(data_domain)
    # END WITH
# END test__create_data_domain_with_wrong_qualified_name


def test__data_domain_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    data_domain = {
        "name": "data domain",
        "qualifiedName": "data-domain",
        "definition": "definition"
    }

    instance = DataDomain.from_dict(data_domain)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.qualified_name == instance.qualified_name
# END test__data_domain_convert_to_atlas_entity


def test__data_domain_convert_to_atlas_entity_with_domain_lead():
    """
    Tests whether or not the `business_owner` field is correctly converted to the atlas format.
    """

    data_domain = {
        "name": "data domain",
        "qualifiedName": "data-domain",
        "domainLead": "domain lead",
        "source": "source-name"
    }

    instance = DataDomain.from_dict(data_domain)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_domain_lead = atlas_attributes.domain_lead[0]

    assert atlas_domain_lead is not None
    assert atlas_domain_lead.type_name == "m4i_person"
    assert getattr(atlas_domain_lead.unique_attributes,
                   "qualified_name") == instance.domain_lead

    atlas_domain_source = atlas_attributes.source[0]

    assert atlas_domain_source is not None
    assert atlas_domain_source.type_name == "m4i_source"
    assert getattr(atlas_domain_source.unique_attributes,
                   "qualified_name") == instance.source
# END test__data_domain_convert_to_atlas_entity_with_domain_lead
