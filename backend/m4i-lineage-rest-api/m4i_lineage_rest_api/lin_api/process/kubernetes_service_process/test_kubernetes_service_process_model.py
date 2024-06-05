import json
import pytest

from .kubernetes_service_process_model import KubernetesServiceProcess


@pytest.fixture
def kubernetes_service_process():
    return {
        "qualifiedName": "testing_m4i_kubernetes_service_process",
        "name": "testing_m4i_kubernetes_service_process",
        "description": "test_m4i_kubernetes_service_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "ingressObject": "test_m4i_ingress_object_process",
        "namespace": "test_m4i_kubernetes_namespace",
        "microservice": ["test_m4i_microservice_process"]
    }


def test__create_kubernetes_service_process_from_dict(kubernetes_service_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """
    instance = KubernetesServiceProcess.from_dict(kubernetes_service_process)

    assert instance.qualified_name == "testing_m4i_kubernetes_service_process"
    assert instance.name == "testing_m4i_kubernetes_service_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_kubernetes_service_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_object == "test_m4i_ingress_object_process"
    assert instance.namespace == "test_m4i_kubernetes_namespace"
    assert instance.microservice == ["test_m4i_microservice_process"]


# END test__create_kubernetes_service_process_from_dict


def test__create_kubernetes_service_process_from_json(kubernetes_service_process):
    """
    Tests whether or not a `connector process` can be created from a dict with its attributes
    """

    kubernetes_service_process = json.dumps(kubernetes_service_process)

    instance = KubernetesServiceProcess.from_json(kubernetes_service_process)

    assert instance.qualified_name == "testing_m4i_kubernetes_service_process"
    assert instance.name == "testing_m4i_kubernetes_service_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "test_m4i_kubernetes_service_process"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.ingress_object == "test_m4i_ingress_object_process"
    assert instance.namespace == "test_m4i_kubernetes_namespace"
    assert instance.microservice == ["test_m4i_microservice_process"]


# END test__create_kubernetes_service_process_from_json


def test__kubernetes_service_process_convert_to_atlas_entity(kubernetes_service_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesServiceProcess.from_dict(kubernetes_service_process)

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
    assert getattr(atlas_ingress_object.unique_attributes, "qualified_name") == instance.ingress_object

    atlas_microservice = atlas_attributes.microservice[0]
    assert atlas_microservice is not None
    assert getattr(atlas_microservice.unique_attributes, "qualified_name") == instance.microservice[0]

    atlas_namespace = atlas_instance.relationship_attributes.namespace[0]
    assert atlas_namespace is not None
    assert getattr(atlas_namespace.unique_attributes, "qualified_name") == instance.namespace

# END test__kubernetes_service_process_convert_to_atlas_entity
