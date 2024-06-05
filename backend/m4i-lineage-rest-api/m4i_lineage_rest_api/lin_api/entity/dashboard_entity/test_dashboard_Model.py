import pytest

from .dashboard_Model import Dashboard


def test__create_dashboard_from_dict():
    """
    Tests whether or not a `Dashboard` can be created from a dict with its attributes
    """

    dashboard = {
        "qualifiedName": "test_m4i_dashboard_entity",
        "name": "test_m4i_dashboard_entity",
        "description": "asda",
        "updatedAt": "updatedAT",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = Dashboard.from_dict(dashboard)

    assert instance.name == "test_m4i_dashboard_entity"
    assert instance._qualified_name() == "test_m4i_dashboard_entity"


# END test__create_dashboard_from_dict


def test__create_dashboard_from_json():
    """
    Tests whether or not a `Dashboard` can be created from a json string with its attributes
    """

    dashboard = (
        """
        {
            "qualifiedName": "dashboard",
            "name": "Dashboard",
            "description": "description",
            "updatedAt": "updatedAt",
            "version": "VERSION",
            "kibanaSpace": "test_m4i_kibana_space",
            "creator": [
                "test_m4i_person"
            ],
            "child_dataset": [
                "tester_m4i_visualization"
            ]
        }
        """
    )

    instance = Dashboard.from_json(dashboard)

    assert instance.name == "Dashboard"
    assert instance._qualified_name() == "dashboard"
    assert instance.description == "description"
    assert instance.updated_at == "updatedAt"


# END test__create_dashboard_from_json


def test__dashboard_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    dashboard = {
        "name": "dashboard",
        "qualifiedName": "dashboard"
    }

    instance = Dashboard.from_dict(dashboard)

    assert instance._qualified_name() == "dashboard"


# END test__dashboard_calculates_correct_qualified_name


def test__dashboard_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    dashboard = {
        "qualifiedName": "dashboard",
        "name": "Dashboard",
        "description": "description",
        "updatedAt": "updatedAt",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = Dashboard.from_dict(dashboard)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.updated_at == instance.updated_at
    assert atlas_attributes.version == instance.version
    assert atlas_attributes.qualified_name == instance._qualified_name()


# END test__dashboard_convert_to_atlas_entity


def test__dashboard_convert_to_atlas_entity_with_kibana_space():
    """
    Tests whether or not the `kibana_space` field is correctly converted to the atlas format.
    """

    dashboard = {
        "qualifiedName": "dashboard",
        "name": "Dashboard",
        "description": "description",
        "updatedAt": "updatedAt",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = Dashboard.from_dict(dashboard)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_kibana_space = atlas_attributes.kibana_space[0]

    assert atlas_kibana_space is not None
    assert atlas_kibana_space.type_name == "m4i_kibana_space"
    assert getattr(atlas_kibana_space.unique_attributes,
                   "qualified_name") == instance.kibana_space


# END test__dashboard_convert_to_atlas_entity_with_kibana_space


def test__dashboard_convert_to_atlas_entity_with_creator():
    """
    Tests whether or not the `Creator` field is correctly converted to the atlas format.
    """

    dashboard = {
        "qualifiedName": "dashboard",
        "name": "Dashboard",
        "description": "description",
        "updatedAt": "updatedAt",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = Dashboard.from_dict(dashboard)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_person = atlas_attributes.creator

    for person in atlas_person:
        assert person is not None
        assert person.type_name == "m4i_person"
        assert getattr(person.unique_attributes,
                       "qualified_name") == instance.creator[0]


# END test__dashboard_convert_to_atlas_entity_with_creator

def test__dashboard_convert_to_atlas_entity_with_dataset():
    """
    Tests whether or not the `Child Dataset` field is correctly converted to the atlas format.
    """

    dashboard = {
        "qualifiedName": "dashboard",
        "name": "Dashboard",
        "description": "description",
        "updatedAt": "updatedAt",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "tester_m4i_visualization"
        ]
    }

    instance = Dashboard.from_dict(dashboard)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_dataset = atlas_attributes.child_dataset

    for dataset in atlas_dataset:
        assert dataset is not None
        assert dataset.type_name == "m4i_visualization"
        assert getattr(dataset.unique_attributes,
                       "qualified_name") == instance.child_dataset[0]
# END test__dashboard_convert_to_atlas_entity_with_dataset
