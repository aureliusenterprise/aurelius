import json
import pytest

from .kubernetes_namespace_model import KubernetesNamespace


@pytest.fixture
def kubernetes_namespace():
    return {
        "qualifiedName": "testing_m4i_kubernetes_namespace",
        "name": "test_m4i_kubernetes_namespace",
        "description": "something",
        "kubernetesCluster": "test_m4i_kubernetes_cluster",
        "kubernetesCronjob": ["test_m4i_kubernetes_cronjob"],
        "kubernetesDeployment": ["test_m4i_kubernetes_deployment"],
    }


def test__create_kubernetes_namespace_from_dict(kubernetes_namespace):
    """
    Tests whether or not a `Kubernetes Namespace` can be created from a dict with its attributes
    """

    instance = KubernetesNamespace.from_dict(kubernetes_namespace)

    assert instance.qualified_name == "testing_m4i_kubernetes_namespace"
    assert instance.name == "test_m4i_kubernetes_namespace"
    assert instance.description == "something"
    assert instance.kubernetes_cluster == "test_m4i_kubernetes_cluster"
    assert instance.kubernetes_deployment[0] == "test_m4i_kubernetes_deployment"
    assert instance.kubernetes_cronjob[0] == "test_m4i_kubernetes_cronjob"


# END test__create_kubernetes_namespace_from_dict


def test__create_kubernetes_namespace_from_json(kubernetes_namespace):
    """
    Tests whether or not a `Kubernetes Namespace` can be created from a dict with its attributes
    """

    kubernetes_namespace = json.dumps(kubernetes_namespace)

    instance = KubernetesNamespace.from_json(kubernetes_namespace)

    assert instance.qualified_name == "testing_m4i_kubernetes_namespace"
    assert instance.name == "test_m4i_kubernetes_namespace"
    assert instance.description == "something"
    assert instance.kubernetes_cluster == "test_m4i_kubernetes_cluster"
    assert instance.kubernetes_deployment[0] == "test_m4i_kubernetes_deployment"
    assert instance.kubernetes_cronjob[0] == "test_m4i_kubernetes_cronjob"


# END test__create_kubernetes_namespace_from_json


def test__kubernetes_namespace_convert_to_atlas_entity(kubernetes_namespace):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesNamespace.from_dict(kubernetes_namespace)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description

    atlas_kubernetes_deployment = atlas_attributes.kubernetes_deployment[0]
    assert atlas_kubernetes_deployment is not None
    assert getattr(atlas_kubernetes_deployment.unique_attributes, "qualified_name") == instance.kubernetes_deployment[0]

    atlas_kubernetes_cronjob = atlas_attributes.kubernetes_cronjob[0]
    assert atlas_kubernetes_cronjob is not None
    assert getattr(atlas_kubernetes_cronjob.unique_attributes, "qualified_name") == instance.kubernetes_cronjob[0]

    atlas_kubernetes_cluster = atlas_attributes.kubernetes_cluster[0]
    assert atlas_kubernetes_cluster is not None
    assert getattr(atlas_kubernetes_cluster.unique_attributes, "qualified_name") == instance.kubernetes_cluster

# END test__kubernetes_namespace_convert_to_atlas_entity
