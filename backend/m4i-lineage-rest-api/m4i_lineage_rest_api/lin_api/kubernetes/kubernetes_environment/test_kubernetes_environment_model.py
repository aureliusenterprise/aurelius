import json
import pytest

from .kubernetes_environment_model import KubernetesEnvironment


@pytest.fixture
def kubernetes_environment():
    return {
        "qualifiedName": "testing_m4i_kubernetes_environment",
        "name": "test_m4i_kubernetes_environment",
        "kubernetesClusters": ["test_m4i_kubernetes_cluster"],
        "description": "something",
    }


def test__create_kubernetes_environment_from_dict(kubernetes_environment):
    """
    Tests whether or not a `Kubernetes Environment` can be created from a dict with its attributes
    """

    instance = KubernetesEnvironment.from_dict(kubernetes_environment)

    assert instance.qualified_name == "testing_m4i_kubernetes_environment"
    assert instance.name == "test_m4i_kubernetes_environment"
    assert instance.description == "something"
    assert instance.kubernetes_clusters[0] == "test_m4i_kubernetes_cluster"


# END test__create_kubernetes_environment_from_dict


def test__create_kubernetes_environment_from_json(kubernetes_environment):
    """
    Tests whether or not a `Kubernetes Environment` can be created from a dict with its attributes
    """

    kubernetes_environment = json.dumps(kubernetes_environment)

    instance = KubernetesEnvironment.from_json(kubernetes_environment)

    assert instance.qualified_name == "testing_m4i_kubernetes_environment"
    assert instance.name == "test_m4i_kubernetes_environment"
    assert instance.description == "something"
    assert instance.kubernetes_clusters[0] == "test_m4i_kubernetes_cluster"


# END test__create_kubernetes_environment_from_json


def test__kubernetes_environment_convert_to_atlas_entity(kubernetes_environment):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesEnvironment.from_dict(kubernetes_environment)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description

    atlas_kubernetes_clusters = atlas_attributes.kubernetes_clusters[0]
    assert atlas_kubernetes_clusters is not None
    assert getattr(atlas_kubernetes_clusters.unique_attributes, "qualified_name") == instance.kubernetes_clusters[0]

# END test__kubernetes_environment_convert_to_atlas_entity
