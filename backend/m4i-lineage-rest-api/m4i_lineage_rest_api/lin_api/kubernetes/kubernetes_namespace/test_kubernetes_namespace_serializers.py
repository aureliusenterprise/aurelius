import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_kubernetes_namespace",
        "name": "test_m4i_kubernetes_namespace",
        "description": "something",
        "kubernetesCluster": "test_m4i_kubernetes_cluster",
        "kubernetesCronjob": ["test_m4i_kubernetes_cronjob"],
        "kubernetesDeployment": ["test_m4i_kubernetes_deployment"],
    }


path = '/lin_api/kubernetes/kubernetes_namespace/'
entity_qn = "testing_m4i_kubernetes_namespace"
entity_type = "m4i_kubernetes_namespace"


def test_m4i_kubernetes_cluster_model_no_kubernetes_cluster(client, request_to_make):
    request_no_kubernetes_cluster = request_to_make.copy()
    request_no_kubernetes_cluster.pop('kubernetesCluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesCluster": "'kubernetesCluster' is a required property"}


# END test_m4i_kubernetes_cluster_model_no_kubernetes_cluster

def test_m4i_kubernetes_cluster_model_no_kubernetes_cronjob(client, request_to_make):
    request_no_kubernetes_cronjob = request_to_make.copy()
    request_no_kubernetes_cronjob.pop('kubernetesCronjob')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_cronjob)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesCronjob": "'kubernetesCronjob' is a required property"}


# END test_m4i_kubernetes_cluster_model_no_kubernetes_cronjob


def test_m4i_kubernetes_cluster_model_empty_kubernetes_cronjob(client, request_to_make, check_made, cleanup):
    request_empty_kubernetes_cronjob = request_to_make.copy()
    request_empty_kubernetes_cronjob['kubernetesCronjob'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_kubernetes_cronjob)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_kubernetes_cluster_model_empty_kubernetes_cronjob


def test_m4i_kubernetes_cluster_model_no_kubernetes_deployment(client, request_to_make):
    request_no_kubernetes_deployment = request_to_make.copy()
    request_no_kubernetes_deployment.pop('kubernetesDeployment')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_deployment)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesDeployment": "'kubernetesDeployment' is a required property"}


# END test_m4i_kubernetes_cluster_model_no_kubernetes_deployment


def test_m4i_kubernetes_cluster_model_empty_kubernetes_deployment(client, request_to_make, check_made, cleanup):
    request_empty_kubernetes_deployment = request_to_make.copy()
    request_empty_kubernetes_deployment['kubernetesDeployment'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_kubernetes_deployment)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kubernetes_cluster_model_empty_kubernetes_deployment
