import json
import pytest

from .ingress_controller_process_model import IngressControllerProcess


@pytest.fixture
def ingress_controller_process():
    return {
        "qualifiedName": "testing_m4i_ingress_controller_process",
        "name": "testing_m4i_ingress_controller_process",
        "description": "test_m4i_ingress_controller_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "ingressObject": [
            "test_m4i_ingress_object_process"
        ],
        "cluster": "test_m4i_kubernetes_cluster"
    }


def test__create_ingress_controller_process_from_dict(ingress_controller_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """
    instance = IngressControllerProcess.from_dict(ingress_controller_process)

    assert instance.qualified_name == "testing_m4i_ingress_controller_process"
    assert instance.name == "testing_m4i_ingress_controller_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_ingress_controller_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_object == ["test_m4i_ingress_object_process"]
    assert instance.cluster == "test_m4i_kubernetes_cluster"


# END test__create_ingress_controller_process_from_dict


def test__create_ingress_controller_process_from_json(ingress_controller_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    ingress_controller_process = json.dumps(ingress_controller_process)

    instance = IngressControllerProcess.from_json(ingress_controller_process)

    assert instance.qualified_name == "testing_m4i_ingress_controller_process"
    assert instance.name == "testing_m4i_ingress_controller_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_ingress_controller_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_object == ["test_m4i_ingress_object_process"]
    assert instance.cluster == "test_m4i_kubernetes_cluster"


# END test__create_ingress_controller_process_from_json


def test__ingress_controller_process_convert_to_atlas_entity(ingress_controller_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = IngressControllerProcess.from_dict(ingress_controller_process)

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

    atlas_ingress_object = atlas_attributes.ingress_object[0]
    assert atlas_ingress_object is not None
    assert getattr(atlas_ingress_object.unique_attributes, "qualified_name") == instance.ingress_object[0]

    atlas_cluster = atlas_instance.relationship_attributes.cluster[0]
    assert atlas_cluster is not None
    assert getattr(atlas_cluster.unique_attributes, "qualified_name") == instance.cluster

# END test__ingress_controller_process_convert_to_atlas_entity
