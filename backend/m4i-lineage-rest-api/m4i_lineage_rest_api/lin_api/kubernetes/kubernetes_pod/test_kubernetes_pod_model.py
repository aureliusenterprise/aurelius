import json
import pytest

from .kubernetes_pod_model import KubernetesPod


@pytest.fixture
def kubernetes_pod():
    return {
        "qualifiedName": "testing_m4i_kubernetes_pod",
        "name": "test_m4i_kubernetes_pod",
        "description": "something",
        "replicas": "2",
        "kubernetesCronjob": "test_m4i_kubernetes_cronjob",
        "kubernetesDeployment": "test_m4i_kubernetes_deployment",
    }


def test__create_kubernetes_pod_from_dict(kubernetes_pod):
    """
    Tests whether or not a `Kubernetes Pod` can be created from a dict with its attributes
    """

    instance = KubernetesPod.from_dict(kubernetes_pod)

    assert instance.qualified_name == "testing_m4i_kubernetes_pod"
    assert instance.name == "test_m4i_kubernetes_pod"
    assert instance.description == "something"
    assert instance.replicas == "2"
    assert instance.kubernetes_deployment == "test_m4i_kubernetes_deployment"
    assert instance.kubernetes_cronjob == "test_m4i_kubernetes_cronjob"


# END test__create_kubernetes_pod_from_dict


def test__create_kubernetes_pod_from_json(kubernetes_pod):
    """
    Tests whether or not a `Kubernetes Pod` can be created from a dict with its attributes
    """

    kubernetes_pod = json.dumps(kubernetes_pod)

    instance = KubernetesPod.from_json(kubernetes_pod)

    assert instance.qualified_name == "testing_m4i_kubernetes_pod"
    assert instance.name == "test_m4i_kubernetes_pod"
    assert instance.description == "something"
    assert instance.replicas == "2"
    assert instance.kubernetes_deployment == "test_m4i_kubernetes_deployment"
    assert instance.kubernetes_cronjob == "test_m4i_kubernetes_cronjob"


# END test__create_kubernetes_pod_from_json


def test__kubernetes_pod_convert_to_atlas_entity(kubernetes_pod):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesPod.from_dict(kubernetes_pod)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description
    assert atlas_attributes.replicas == instance.replicas

    atlas_kubernetes_deployment = atlas_attributes.kubernetes_deployment[0]
    assert atlas_kubernetes_deployment is not None
    assert getattr(atlas_kubernetes_deployment.unique_attributes, "qualified_name") == instance.kubernetes_deployment

    atlas_kubernetes_cronjob = atlas_attributes.kubernetes_cronjob[0]
    assert atlas_kubernetes_cronjob is not None
    assert getattr(atlas_kubernetes_cronjob.unique_attributes, "qualified_name") == instance.kubernetes_cronjob

# END test__kubernetes_pod_convert_to_atlas_entity
