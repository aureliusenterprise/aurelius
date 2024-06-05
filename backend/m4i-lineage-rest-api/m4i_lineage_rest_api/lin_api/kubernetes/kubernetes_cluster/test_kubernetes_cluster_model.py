import json
import pytest

from .kubernetes_cluster_model import KubernetesCluster


@pytest.fixture
def kubernetes_cluster():
    return {
        "qualifiedName": "testing_m4i_kubernetes_cluster",
        "name": "test_m4i_kubernetes_cluster",
        "description": "something",
        "kubernetesEnvironment": "test_m4i_kubernetes_environment",
        "kubernetesNamespace": ["test_m4i_kubernetes_namespace"],
    }


def test__create_kubernetes_cluster_from_dict(kubernetes_cluster):
    """
    Tests whether or not a `Kubernetes Environment` can be created from a dict with its attributes
    """

    instance = KubernetesCluster.from_dict(kubernetes_cluster)

    assert instance.qualified_name == "testing_m4i_kubernetes_cluster"
    assert instance.name == "test_m4i_kubernetes_cluster"
    assert instance.description == "something"
    assert instance.kubernetes_namespace[0] == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_environment == "test_m4i_kubernetes_environment"


# END test__create_kubernetes_cluster_from_dict


def test__create_kubernetes_cluster_from_json(kubernetes_cluster):
    """
    Tests whether or not a `Kubernetes Environment` can be created from a dict with its attributes
    """

    kubernetes_cluster = json.dumps(kubernetes_cluster)

    instance = KubernetesCluster.from_json(kubernetes_cluster)

    assert instance.qualified_name == "testing_m4i_kubernetes_cluster"
    assert instance.name == "test_m4i_kubernetes_cluster"
    assert instance.description == "something"
    assert instance.kubernetes_namespace[0] == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_environment == "test_m4i_kubernetes_environment"


# END test__create_kubernetes_cluster_from_json


def test__kubernetes_cluster_convert_to_atlas_entity(kubernetes_cluster):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesCluster.from_dict(kubernetes_cluster)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description

    atlas_kubernetes_namespace = atlas_attributes.kubernetes_namespace[0]
    assert atlas_kubernetes_namespace is not None
    assert getattr(atlas_kubernetes_namespace.unique_attributes, "qualified_name") == instance.kubernetes_namespace[0]

    atlas_kubernetes_environment = atlas_attributes.kubernetes_environment[0]
    assert atlas_kubernetes_environment is not None
    assert getattr(atlas_kubernetes_environment.unique_attributes, "qualified_name") == instance.kubernetes_environment

# END test__kubernetes_cluster_convert_to_atlas_entity
