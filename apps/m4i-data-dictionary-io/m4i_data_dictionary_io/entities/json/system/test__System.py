import pytest

from .System import System
from ..exceptions import QualifiedNameNotValidException


def test__create_system_from_dict():
    """
    Tests whether or not a `System` can be created from a dict with its attributes
    """

    system = {
        "definition": "definition",
        "name": "system",
        "qualifiedName": "system",
        "source": "source"
    }

    instance = System.from_dict(system)

    assert instance.definition == "definition"
    assert instance.name == "system"
    assert instance.qualified_name == "system"
    assert instance.source == "source"
# END test__create_system_from_dict


def test__create_system_from_json():
    """
    Tests whether or not a `System` can be created from a json string with its attributes
    """

    system = (
        """
        {
            "definition": "definition",
            "name": "system",
            "qualifiedName": "system",
            "source": "source"
        }
        """
    )

    instance = System.from_json(system)

    assert instance.definition == "definition"
    assert instance.name == "system"
    assert instance.qualified_name == "system"
    assert instance.source == "source"
# END test__create_system_from_json


def test__system_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    system = {
        "name": "system",
        "qualifiedName": "system"
    }

    instance = System.from_dict(system)

    assert instance._qualified_name() == "system"
# END test__system_calculates_correct_qualified_name


def test__create_system_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    system = {
        "name": "system",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        System.from_dict(system)
    # END WITH
# END test__create_system_with_wrong_qualified_name


def test__system_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    system = {
        "definition": "definition",
        "name": "system",
        "qualifiedName": "system",
        "source": "source"
    }

    instance = System.from_dict(system)

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

# END test__system_convert_to_atlas_entity
