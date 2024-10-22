import pytest

from .Source import Source
from ..exceptions import QualifiedNameNotValidException


def test__create_source_from_dict():
    """
    Tests whether or not a `Source` can be created from a dict with its attributes
    """

    source = {
        "hash_code": "hash_code",
        "branch": "branch",
        "name": "//folder//dept//Data Dictionary.xlsm",
        "qualifiedName": "//folder//dept//Data Dictionary.xlsm@branch@hash_code",
    }

    instance = Source.from_dict(source)

    assert instance.hash_code == "hash_code"
    assert instance.name == "//folder//dept//Data Dictionary.xlsm"
    assert instance.qualified_name == "//folder//dept//Data Dictionary.xlsm@branch@hash_code"
    assert instance.branch == "branch"


# END test__create_source_from_dict


def test__create_source_from_json():
    """
    Tests whether or not a `Source` can be created from a json string with its attributes
    """

    source = (
        """
        {
            "hash_code": "hash_code",
            "branch": "branch",
            "name": "//folder//dept//Data Dictionary.xlsm",
            "qualifiedName": "//folder//dept//Data Dictionary.xlsm@branch@hash_code"
        }
        """
    )

    instance = Source.from_json(source)

    assert instance.hash_code == "hash_code"
    assert instance.name == "//folder//dept//Data Dictionary.xlsm"
    assert instance.qualified_name == "//folder//dept//Data Dictionary.xlsm@branch@hash_code"
    assert instance.branch == "branch"


# END test__create_source_from_json


def test__source_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    source = {
        "hash_code": "hash_code",
        "branch": "branch",
        "name": "//folder//dept//Data Dictionary.xlsm",
        "qualifiedName": "//folder//dept//Data Dictionary.xlsm@branch@hash_code"
    }

    instance = Source.from_dict(source)

    assert instance._qualified_name() == "//folder//dept//Data Dictionary.xlsm@branch@hash_code"


# END test__source_calculates_correct_qualified_name


def test__create_source_with_wrong_qualified_name():
    """
    Tests whether or not an exception is raised when the qualified name is not valid
    """

    source = {
        "hash_code": "hash_code",
        "branch": "branch",
        "name": "//folder//dept//Data Dictionary.xlsm",
        "qualifiedName": "test",
    }

    with pytest.raises(QualifiedNameNotValidException):
        Source.from_dict(source)
    # END WITH


# END test__create_source_with_wrong_qualified_name


def test__source_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    source = {
        "hash_code": "hash_code",
        "branch": "branch",
        "name": "//folder//dept//Data Dictionary.xlsm",
        "qualifiedName": "//folder//dept//Data Dictionary.xlsm@branch@hash_code"
    }

    instance = Source.from_dict(source)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.hash_code == instance.hash_code
    assert atlas_attributes.branch == instance.branch
    assert atlas_attributes.qualified_name == instance.qualified_name
# END test__source_convert_to_atlas_entity
