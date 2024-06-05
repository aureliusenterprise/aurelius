import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_kubernetes_cluster",
        "name": "test_m4i_kubernetes_cluster",
        "description": "something",
        "kubernetesEnvironment": "test_m4i_kubernetes_environment",
        "kubernetesNamespace": ["test_m4i_kubernetes_namespace"],
    }


path = '/lin_api/kubernetes/kubernetes_cluster/'
entity_qn = "testing_m4i_kubernetes_cluster"
entity_type = "m4i_kubernetes_cluster"


def test_m4i_kubernetes_cluster_model_no_kubernetes_environment(client, request_to_make):
    request_no_kubernetes_environment = request_to_make.copy()
    request_no_kubernetes_environment.pop('kubernetesEnvironment')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_environment)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesEnvironment": "'kubernetesEnvironment' is a required property"}


# END test_m4i_kubernetes_cluster_model_no_kubernetes_environment

def test_m4i_kubernetes_cluster_model_no_kubernetes_namespace(client, request_to_make):
    request_no_kubernetes_namespace = request_to_make.copy()
    request_no_kubernetes_namespace.pop('kubernetesNamespace')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_namespace)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesNamespace": "'kubernetesNamespace' is a required property"}


# END test_m4i_kubernetes_cluster_model_no_kubernetes_namespace


def test_m4i_kubernetes_cluster_model_empty_kubernetes_namespace(client, request_to_make, check_made, cleanup):
    request_empty_kubernetes_namespace = request_to_make.copy()
    request_empty_kubernetes_namespace['kubernetesNamespace'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_kubernetes_namespace)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kubernetes_cluster_model_empty_kubernetes_namespace
