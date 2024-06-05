import json
import pytest

from .kubernetes_cronjob_model import KubernetesCronjob


@pytest.fixture
def kubernetes_cronjob():
    return {
        "qualifiedName": "testing_m4i_kubernetes_cronjob",
        "name": "test_m4i_kubernetes_cronjob",
        "description": "something",
        "kubernetesNamespace": "test_m4i_kubernetes_namespace",
        "kubernetesPod": ["test_m4i_kubernetes_pod"],
        "tags": "Tag",
        "schedule": "date--time"
    }


def test__create_kubernetes_cronjob_from_dict(kubernetes_cronjob):
    """
    Tests whether or not a `Kubernetes Cronjob` can be created from a dict with its attributes
    """

    instance = KubernetesCronjob.from_dict(kubernetes_cronjob)

    assert instance.qualified_name == "testing_m4i_kubernetes_cronjob"
    assert instance.name == "test_m4i_kubernetes_cronjob"
    assert instance.description == "something"
    assert instance.kubernetes_namespace == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_pod[0] == "test_m4i_kubernetes_pod"
    assert instance.tags == "Tag"
    assert instance.schedule == "date--time"


# END test__create_kubernetes_cronjob_from_dict


def test__create_kubernetes_cronjob_from_json(kubernetes_cronjob):
    """
    Tests whether or not a `Kubernetes Cronjob` can be created from a dict with its attributes
    """

    kubernetes_cronjob = json.dumps(kubernetes_cronjob)

    instance = KubernetesCronjob.from_json(kubernetes_cronjob)

    assert instance.qualified_name == "testing_m4i_kubernetes_cronjob"
    assert instance.name == "test_m4i_kubernetes_cronjob"
    assert instance.description == "something"
    assert instance.kubernetes_namespace == "test_m4i_kubernetes_namespace"
    assert instance.kubernetes_pod[0] == "test_m4i_kubernetes_pod"
    assert instance.tags == "Tag"
    assert instance.schedule == "date--time"


# END test__create_kubernetes_cronjob_from_json


def test__kubernetes_cronjob_convert_to_atlas_entity(kubernetes_cronjob):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = KubernetesCronjob.from_dict(kubernetes_cronjob)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.definition == instance.description
    assert atlas_attributes.tags == instance.tags
    assert atlas_attributes.schedule == instance.schedule

    atlas_kubernetes_pod = atlas_attributes.kubernetes_pod[0]
    assert atlas_kubernetes_pod is not None
    assert getattr(atlas_kubernetes_pod.unique_attributes, "qualified_name") == instance.kubernetes_pod[0]

    atlas_kubernetes_namespace = atlas_attributes.kubernetes_namespace[0]
    assert atlas_kubernetes_namespace is not None
    assert getattr(atlas_kubernetes_namespace.unique_attributes, "qualified_name") == instance.kubernetes_namespace

# END test__kubernetes_cronjob_convert_to_atlas_entity
