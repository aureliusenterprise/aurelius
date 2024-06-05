import json
import pytest

from .microservice_process_model import MicroserviceProcess


@pytest.fixture
def microservice_process():
    return {
        "qualifiedName": "test_m4i_microservice_process",
        "name": "test_m4i_microservice_process",
        "description": "test_m4i_microservice_process",
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
        "system": "test_m4i_kubernetes_pod"
    }


def test__create_microservice_process_from_dict(microservice_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """
    instance = MicroserviceProcess.from_dict(microservice_process)

    assert instance.qualified_name == "test_m4i_microservice_process"
    assert instance.name == "test_m4i_microservice_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_microservice_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]
    assert instance.system == "test_m4i_kubernetes_pod"


# END test__create_microservice_process_from_dict


def test__create_microservice_process_from_json(microservice_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    microservice_process = json.dumps(microservice_process)

    instance = MicroserviceProcess.from_json(microservice_process)

    assert instance.qualified_name == "test_m4i_microservice_process"
    assert instance.name == "test_m4i_microservice_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_microservice_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]
    assert instance.system == "test_m4i_kubernetes_pod"


# END test__create_microservice_process_from_json


def test__microservice_process_convert_to_atlas_entity(microservice_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = MicroserviceProcess.from_dict(microservice_process)

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

    atlas_system = atlas_attributes.system[0]
    assert atlas_system is not None
    assert getattr(atlas_system.unique_attributes, "qualified_name") == instance.system

# END test__microservice_process_convert_to_atlas_entity
