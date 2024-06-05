import json
import pytest

from .ingress_object_process_model import IngressObjectProcess


@pytest.fixture
def ingress_object_process():
    return {
        "qualifiedName": "testing_m4i_ingress_object_process",
        "name": "testing_m4i_ingress_object_process",
        "description": "test_m4i_ingress_object_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "ingressController": "test_m4i_ingress_controller_process",
        "kubernetesService": [
            "test_m4i_kubernetes_service_process"
        ],
        "namespace": "test_m4i_kubernetes_namespace"
    }


def test__create_ingress_object_process_from_dict(ingress_object_process):
    """
    Tests whether or not a `Ingress Object process` can be created from a dict with its attributes
    """
    instance = IngressObjectProcess.from_dict(ingress_object_process)

    assert instance.qualified_name == "testing_m4i_ingress_object_process"
    assert instance.name == "testing_m4i_ingress_object_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_ingress_object_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_controller == "test_m4i_ingress_controller_process"
    assert instance.kubernetes_service == ["test_m4i_kubernetes_service_process"]
    assert instance.namespace == "test_m4i_kubernetes_namespace"


# END test__create_ingress_object_process_from_dict


def test__create_ingress_object_process_from_json(ingress_object_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    ingress_object_process = json.dumps(ingress_object_process)

    instance = IngressObjectProcess.from_json(ingress_object_process)

    assert instance.qualified_name == "testing_m4i_ingress_object_process"
    assert instance.name == "testing_m4i_ingress_object_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_ingress_object_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_controller == "test_m4i_ingress_controller_process"
    assert instance.kubernetes_service == ["test_m4i_kubernetes_service_process"]
    assert instance.namespace == "test_m4i_kubernetes_namespace"


# END test__create_ingress_object_process_from_json


def test__ingress_object_process_convert_to_atlas_entity(ingress_object_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = IngressObjectProcess.from_dict(ingress_object_process)

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

    atlas_kubernetes_service = atlas_attributes.kubernetes_service[0]
    assert atlas_kubernetes_service is not None
    assert getattr(atlas_kubernetes_service.unique_attributes, "qualified_name") == instance.kubernetes_service[0]

    atlas_ingress_controller = atlas_attributes.ingress_controller[0]
    assert atlas_ingress_controller is not None
    assert getattr(atlas_ingress_controller.unique_attributes, "qualified_name") == instance.ingress_controller

    atlas_namespace = atlas_instance.relationship_attributes.namespace[0]
    assert atlas_namespace is not None
    assert getattr(atlas_namespace.unique_attributes, "qualified_name") == instance.namespace

# END test__ingress_object_process_convert_to_atlas_entity
