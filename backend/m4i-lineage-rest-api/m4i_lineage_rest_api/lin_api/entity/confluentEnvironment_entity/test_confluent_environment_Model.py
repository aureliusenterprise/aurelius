from .confluentEnvironment_Model import ConfluentEnvironment


def test__create_confluent_env_from_dict():
    """
    Tests whether or not a `ConfluentEnvironment` can be created from a dict with its attributes
    """

    confluent_env = {
        "name": "confluent_environment",
        "schema_registry": "true",
        "confluent_cloud": "confluent_cloud"
    }

    instance = ConfluentEnvironment.from_dict(confluent_env)

    assert instance.name == "confluent_environment"
    assert instance.schema_registry == "true"
    assert instance.confluent_cloud == "confluent_cloud"
    assert instance._qualified_name() == "confluent_cloud--confluent_environment"


# END test__create_confluent_environment_from_dict

def test__create_confluent_environment_from_json():
    """
    Tests whether or not a `ConfluentEnvironment` can be created from a json string with its attributes
    """

    confluent_environment = (
        """
        {
            "name": "confluent_environment",
            "schema_registry": "true",
            "confluent_cloud": "confluent_cloud"
         }   
        """
    )

    instance = ConfluentEnvironment.from_json(confluent_environment)

    assert instance.name == "confluent_environment"
    assert instance._qualified_name() == "confluent_cloud--confluent_environment"
    assert bool(instance.schema_registry) == True


# END test__create_confluent_environment_from_json


def test__confluent_environment_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    confluent_environment = {
        "name": "confluent_environment",
        "confluent_cloud": "confluent_cloud"
    }

    instance = ConfluentEnvironment.from_dict(confluent_environment)

    assert instance._qualified_name() == "confluent_cloud--confluent_environment"


# END test__confluent_environment_calculates_correct_qualified_name


def test__confluent_environment_convert_to_atlas_entity_with_confluent_cloud():
    """
    Tests whether or not the `confluent_cloud` field is correctly converted to the atlas format.
    """

    confluent_environment = {
        "name": "confluent_environment",
        "schema_registry": "true",
        "confluent_cloud": "confluent_cloud"
    }

    instance = ConfluentEnvironment.from_dict(confluent_environment)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_confluent_cloud = atlas_attributes.confluent_cloud[0]

    assert atlas_confluent_cloud is not None
    assert atlas_confluent_cloud.type_name == "m4i_confluent_cloud"
    assert getattr(atlas_confluent_cloud.unique_attributes,
                   "qualified_name") == instance.confluent_cloud
# END test__confluent_environment_convert_to_atlas_entity_with_confluent_cloud
