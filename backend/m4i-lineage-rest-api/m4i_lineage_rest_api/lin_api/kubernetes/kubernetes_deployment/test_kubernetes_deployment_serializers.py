import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_kubernetes_deployment",
        "name": "test_m4i_kubernetes_deployment",
        "description": "something",
        "kubernetesNamespace": "test_m4i_kubernetes_namespace",
        "kubernetesPod": ["test_m4i_kubernetes_pod"],
        "tags": "Tag",
    }


path = '/lin_api/kubernetes/kubernetes_deployment/'
entity_qn = "testing_m4i_kubernetes_deployment"
entity_type = "m4i_kubernetes_deployment"


def test_m4i_kubernetes_deployment_model_no_kubernetes_cluster(client, request_to_make):
    request_no_kubernetes_namespace = request_to_make.copy()
    request_no_kubernetes_namespace.pop('kubernetesNamespace')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_namespace)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesNamespace": "'kubernetesNamespace' is a required property"}


# END test_m4i_kubernetes_deployment_model_no_kubernetes_namespace

def test_m4i_kubernetes_deployment_model_no_kubernetes_pod(client, request_to_make):
    request_no_kubernetes_pod = request_to_make.copy()
    request_no_kubernetes_pod.pop('kubernetesPod')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_pod)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesPod": "'kubernetesPod' is a required property"}


# END test_m4i_kubernetes_deployment_model_no_kubernetes_pod


def test_m4i_kubernetes_deployment_model_empty_kubernetes_pod(client, request_to_make, check_made, cleanup):
    request_empty_kubernetes_pod = request_to_make.copy()
    request_empty_kubernetes_pod['kubernetesPod'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_kubernetes_pod)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_kubernetes_deployment_model_empty_kubernetes_pod


def test_m4i_kubernetes_deployment_model_no_tags(client, request_to_make, check_made, cleanup):
    request_no_tags = request_to_make.copy()
    request_no_tags.pop('tags')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_tags)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kubernetes_deployment_model_no_tags
