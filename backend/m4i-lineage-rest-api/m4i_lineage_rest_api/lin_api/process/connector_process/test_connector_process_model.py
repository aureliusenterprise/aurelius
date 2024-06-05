import json
import pytest

from .connector_process_model import ConnectorProcess


@pytest.fixture
def connector_process():
    return {
        "qualifiedName": "test_m4i_connector_process",
        "name": "test_m4i_connector_process",
        "description": "test_m4i_connector_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "source": [
            "test_m4i_source"
        ],
        "connectorType": "test_m4i_connector_process Type",
        "server": "test_m4i_connector_process Server"
    }


def test__create_connector_process_from_dict(connector_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """
    instance = ConnectorProcess.from_dict(connector_process)

    assert instance.qualified_name == "test_m4i_connector_process"
    assert instance.name == "test_m4i_connector_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_connector_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]
    assert instance.connector_type == "test_m4i_connector_process Type"
    assert instance.server == "test_m4i_connector_process Server"


# END test__create_connector_process_from_dict


def test__create_connector_process_from_json(connector_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    connector_process = json.dumps(connector_process)

    instance = ConnectorProcess.from_json(connector_process)

    assert instance.qualified_name == "test_m4i_connector_process"
    assert instance.name == "test_m4i_connector_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_connector_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]
    assert instance.connector_type == "test_m4i_connector_process Type"
    assert instance.server == "test_m4i_connector_process Server"


# END test__create_connector_process_from_json


def test__connector_process_convert_to_atlas_entity(connector_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = ConnectorProcess.from_dict(connector_process)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.description == instance.description

    atlas_process_owner = atlas_attributes.process_owner[0]
    assert atlas_process_owner is not None
    assert getattr(atlas_process_owner.unique_attributes, "qualified_name") == instance.process_owner

    atlas_inputs = atlas_attributes.inputs[0]
    assert atlas_inputs is not None
    assert getattr(atlas_inputs.unique_attributes, "qualified_name") == instance.inputs[0]

    atlas_outputs = atlas_attributes.outputs[0]
    assert atlas_outputs is not None
    assert getattr(atlas_outputs.unique_attributes, "qualified_name") == instance.outputs[0]

    atlas_source = atlas_attributes.source[0]
    assert atlas_source is not None
    assert getattr(atlas_source.unique_attributes, "qualified_name") == instance.source[0]

    assert atlas_attributes.connector_type == instance.connector_type
    assert atlas_attributes.server == instance.server

# END test__connector_process_convert_to_atlas_entity
