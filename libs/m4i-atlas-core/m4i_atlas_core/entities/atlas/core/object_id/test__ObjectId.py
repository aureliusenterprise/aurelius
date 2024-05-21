import pytest

from .ObjectId import ObjectId, ObjectIdHasNoReferenceException


def test__create_object_id_from_dict():
    """
    Tests whether or not an `ObjectId` can be created from a dict with its attributes
    """

    object_id = {
        "guid": "guid",
        "typeName": "type name",
        "uniqueAttributes": {
            "qualifiedName": "qualified name"
        }
    }

    instance = ObjectId.from_dict(object_id)

    assert instance.guid == "guid"
    assert instance.type_name == "type name"
    assert instance.unique_attributes.attributes["qualifiedName"] == "qualified name"
# END test__create_data_domain_from_dict


def test__create_object_id_from_json():
    """
    Tests whether or not an `ObjectId` can be created from a json string with its attributes
    """

    object_id = (
        """
        {
            "guid": "guid",
            "typeName": "type name",
            "uniqueAttributes": {
                "qualifiedName": "qualified name"
            }
        }
        """
    )

    instance = ObjectId.from_json(object_id)

    assert instance.guid == "guid"
    assert instance.type_name == "type name"
    assert instance.unique_attributes.attributes["qualifiedName"] == "qualified name"
# END test__create_object_id_from_json


def test__create_object_id_with_guid_only():
    """
    Tests whether or not an `ObjectId` can be created when only specifying a guid
    """

    object_id = {
        "guid": "guid",
        "typeName": "type name"
    }

    ObjectId.from_dict(object_id)
# END test__create_object_id_with_guid_only


def test__create_object_id_with_unique_attributes_only():
    """
    Tests whether or not an `ObjectId` can be created when only specifying a unique attribute
    """

    object_id = {
        "typeName": "type name",
        "uniqueAttributes": {
            "qualifiedName": "qualified name"
        }
    }

    ObjectId.from_dict(object_id)
# END test__create_object_id_with_unique_attributes_only


def test__create_data_attribute_with_missing_reference():
    """
    Tests whether or not an exception is raised when creating an `ObjectId` while no guid or unique attributes are given
    """

    object_id = {
        "typeName": "type name"
    }

    with pytest.raises(ObjectIdHasNoReferenceException):
        ObjectId.from_dict(object_id)
    # END WITH
# END test__create_data_attribute_with_missing_reference


def test__create_object_id_with_empty_unique_attribute():
    """
    Tests whether or not an exception is raised when creating an `ObjectId` while only an empty unique attribute is given
    """

    object_id = {
        "typeName": "type name",
        "uniqueAttributes": {
            "qualifiedName": None
        }
    }

    with pytest.raises(ObjectIdHasNoReferenceException):
        ObjectId.from_dict(object_id)
    # END WITH
# END test__create_object_id_with_empty_unique_attribute
