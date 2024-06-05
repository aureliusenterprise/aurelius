import pytest

from .confluentCloud_Model import ConfluentCloud


def test__create_confluent_cloud_from_dict():
    """
    Tests whether or not a `ConfluentCloud` can be created from a dict with its attributes
    """

    confluent_cloud = {
        "name": "confluent_cloud"
    }

    instance = ConfluentCloud.from_dict(confluent_cloud)

    assert instance.name == "confluent_cloud"
    assert instance._qualified_name() == "confluent_cloud"


# END test__create_confluent_cloud_from_dict


def test__create_confluent_cloud_from_json():
    """
    Tests whether or not a `ConfluentCloud` can be created from a json string with its attributes
    """

    confluent_cloud = (
        """
        {
           "name":"confluent_cloud"
        }
        """
    )

    instance = ConfluentCloud.from_json(confluent_cloud)

    assert instance.name == "confluent_cloud"
    assert instance._qualified_name() == "confluent_cloud"


# END test__create_confluent_cloud_from_json


def test__confluent_cloud_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    confluent_cloud = {
        "name": "confluent_cloud"
    }

    instance = ConfluentCloud.from_dict(confluent_cloud)

    assert instance._qualified_name() == "confluent_cloud"


# END test__confluent_cloud_calculates_correct_qualified_name


def test__confluent_cloud_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    confluent_cloud = {
        "name": "confluent_cloud"
    }

    instance = ConfluentCloud.from_dict(confluent_cloud)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.qualified_name == instance._qualified_name()

# END test__confluent_cloud_convert_to_atlas_entity
