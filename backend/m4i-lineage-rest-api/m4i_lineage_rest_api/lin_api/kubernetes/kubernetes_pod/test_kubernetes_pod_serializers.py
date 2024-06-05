import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_kubernetes_pod",
        "name": "test_m4i_kubernetes_pod",
        "description": "something",
        "replicas": "2",
        "kubernetesCronjob": "test_m4i_kubernetes_cronjob",
        "kubernetesDeployment": "test_m4i_kubernetes_deployment",
    }


path = '/lin_api/kubernetes/kubernetes_pod/'
entity_qn = "testing_m4i_kubernetes_pod"
entity_type = "m4i_kubernetes_pod"


def test_m4i_kubernetes_pod_model_no_kubernetes_cronjob(client, request_to_make, check_made, cleanup):
    request_no_kubernetes_cronjob = request_to_make.copy()
    request_no_kubernetes_cronjob.pop('kubernetesCronjob')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_cronjob)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_kubernetes_pod_model_no_kubernetes_cronjob

def test_m4i_kubernetes_pod_model_no_kubernetes_deployment(client, request_to_make, check_made, cleanup):
    request_no_kubernetes_deployment = request_to_make.copy()
    request_no_kubernetes_deployment.pop('kubernetesDeployment')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_deployment)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_kubernetes_pod_model_no_kubernetes_deployment
def test_m4i_kubernetes_pod_model_no_replicas(client, request_to_make, check_made, cleanup):
    request_no_replicas = request_to_make.copy()
    request_no_replicas.pop('replicas')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_replicas)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kubernetes_pod_model_no_replicas
