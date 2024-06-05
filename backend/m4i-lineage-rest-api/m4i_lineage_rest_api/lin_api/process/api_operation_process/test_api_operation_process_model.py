import json
import pytest

from .api_operation_process_model import ApiOperationProcess


@pytest.fixture
def api_operation_process():
    return {
        "qualifiedName": "testing_m4i_api_operation_process",
        "name": "testing_m4i_api_operation_process",
        "description": "test_m4i_api_operation_process",
        "microservice": "test_m4i_microservice_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ]
    }


def test__create_api_operation_process_from_dict(api_operation_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """
    instance = ApiOperationProcess.from_dict(api_operation_process)

    assert instance.qualified_name == "testing_m4i_api_operation_process"
    assert instance.name == "testing_m4i_api_operation_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_api_operation_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.microservice == "test_m4i_microservice_process"


# END test__create_api_operation_process_from_dict


def test__create_api_operation_process_from_json(api_operation_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    api_operation_process = json.dumps(api_operation_process)

    instance = ApiOperationProcess.from_json(api_operation_process)

    assert instance.qualified_name == "testing_m4i_api_operation_process"
    assert instance.name == "testing_m4i_api_operation_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_api_operation_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.microservice == "test_m4i_microservice_process"


# END test__create_api_operation_process_from_json


def test__api_operation_process_convert_to_atlas_entity(api_operation_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = ApiOperationProcess.from_dict(api_operation_process)

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

    atlas_microservice = atlas_attributes.microservice[0]
    assert atlas_microservice is not None
    assert getattr(atlas_microservice.unique_attributes, "qualified_name") == instance.microservice

# END test__api_operation_process_convert_to_atlas_entity
