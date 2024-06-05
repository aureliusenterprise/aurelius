from .kibanaSpace_Model import KibanaSpace


def test__create_kibana_space_from_dict():
    """
    Tests whether or not a `KibanaSpace` can be created from a dict with its attributes
    """

    kibana_space = {
        "name": "Kibana Space",
        "avatar_color": "avatar_color",
        "avatar_initials": "avatar_initials",
        "elastic_cluster": "elastic_cluster",
        "definition": "definition"
    }

    instance = KibanaSpace.from_dict(kibana_space)

    assert instance.name == "Kibana Space"
    assert instance.avatar_color == "avatar_color"
    assert instance.avatar_initials == "avatar_initials"
    assert instance.elastic_cluster == "elastic_cluster"
    assert instance.definition == "definition"


# END test__create_kibana_space_from_dict


def test__create_kibana_space_from_json():
    """
    Tests whether or not a `kibana_space` can be created from a json string with its attributes
    """

    kibana_space = (
        """
        {
        "name": "name",
        "avatar_color": "avatar_color",
        "avatar_initials": "avatar_initials",
        "elastic_cluster": "elastic_cluster",
        "definition": "definition"
        }
        """
    )

    instance = KibanaSpace.from_json(kibana_space)

    assert instance.name == "name"
    assert instance.avatar_color == "avatar_color"
    assert instance.avatar_initials == "avatar_initials"
    assert instance.elastic_cluster == "elastic_cluster"
    assert instance.definition == "definition"
    assert instance._qualified_name() == "elastic_cluster--name"


# END test__create_kibana_space_from_json


def test__kibana_space_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    kibana_space = {
        "name": "kibana_space",
        "elastic_cluster": "elastic_cluster",
        "qualifiedName": "kibana_space"
    }

    instance = KibanaSpace.from_dict(kibana_space)

    assert instance._qualified_name() == "elastic_cluster--kibana_space"


# END test__kibana_space_calculates_correct_qualified_name


def test__kibana_space_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """
    kibana_space = {
        "definition": "definition",
        "elastic_cluster": "elastic_cluster",
        "name": "kibana_space",
        "qualifiedName": "elastic_cluster--kibana_space"
    }

    instance = KibanaSpace.from_dict(kibana_space)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.definition
    assert atlas_attributes.qualified_name == instance._qualified_name()


# END test__kibana_space_convert_to_atlas_entity

def test__kibana_space_convert_to_atlas_entity_with_elastic_cluster():
    """
    Tests whether or not the `Child Dataset` field is correctly converted to the atlas format.
    """

    kibana_space = {
        "definition": "definition",
        "elastic_cluster": "elastic_cluster",
        "name": "kibana_space",
        "qualifiedName": "elastic_cluster--kibana_space"
    }

    instance = KibanaSpace.from_dict(kibana_space)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_elastic_cluster = atlas_attributes.elastic_cluster[0]

    assert atlas_elastic_cluster is not None
    assert atlas_elastic_cluster.type_name == "m4i_elastic_cluster"
    assert getattr(atlas_elastic_cluster.unique_attributes,
                   "qualified_name") == instance.elastic_cluster
# END test__kibana_space_convert_to_atlas_entity_with_elastic_cluster
