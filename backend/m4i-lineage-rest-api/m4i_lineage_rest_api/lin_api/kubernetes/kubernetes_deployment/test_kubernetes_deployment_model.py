import json
import pytest

from .kubernetes_deployment_model import KubernetesDeployment


@pytest.fixture
def kubernetes_deployment():
    return {
        "qualifiedName": "testing_m4i_kubernetes_deployment",
        "name": "test_m4i_kubernetes_deployment",
        "description": "something",
        "kubernetesNamespace": "test_m4i_kubernetes_namespace",
        "kubernetesPod": ["test_m4i_kubernetes_pod"],
        "tags": "Tag",
    }


def test__create_kubernetes_deployment_from_dict(kubernetes_deployment):
    """
    Tests whether or not a `Kubernetes Deployment` can be created from a dict with its attributes
    """

    instance = KubernetesDeployment.from_dict(kubernetes_deployment)

    assert instance.qualified_name == "testing_m4i_kubernetes_deployment"
    assert instance.name == "test_m4i_kubernetes_deployment"
    assert instance.description == "something"
    assert instance.kubernetes_namespace == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_pod[0] == "test_m4i_kubernetes_pod"
    assert instance.tags == "Tag"


# END test__create_kubernetes_deployment_from_dict


def test__create_kubernetes_deployment_from_json(kubernetes_deployment):
    """
    Tests whether or not a `Kubernetes Deployment` can be created from a dict with its attributes
    """

    kubernetes_deployment = json.dumps(kubernetes_deployment)

    instance = KubernetesDeployment.from_json(kubernetes_deployment)

    assert instance.qualified_name == "testing_m4i_kubernetes_deployment"
    assert instance.name == "test_m4i_kubernetes_deployment"
    assert instance.description == "something"
    assert instance.kubernetes_namespace == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_pod[0] == "test_m4i_kubernetes_pod"
    assert instance.tags == "Tag"


# END test__create_kubernetes_deployment_from_json


def test__kubernetes_deployment_convert_to_atlas_entity(kubernetes_deployment):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesDeployment.from_dict(kubernetes_deployment)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description
    assert atlas_attributes.tags == instance.tags

    atlas_kubernetes_pod = atlas_attributes.kubernetes_pod[0]
    assert atlas_kubernetes_pod is not None
    assert getattr(atlas_kubernetes_pod.unique_attributes, "qualified_name") == instance.kubernetes_pod[0]

    atlas_kubernetes_namespace = atlas_attributes.kubernetes_namespace[0]
    assert atlas_kubernetes_namespace is not None
    assert getattr(atlas_kubernetes_namespace.unique_attributes, "qualified_name") == instance.kubernetes_namespace

# END test__kubernetes_deployment_convert_to_atlas_entity
