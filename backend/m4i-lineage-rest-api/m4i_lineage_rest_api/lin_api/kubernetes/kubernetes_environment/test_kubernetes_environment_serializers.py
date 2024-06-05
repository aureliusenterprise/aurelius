import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_kubernetes_environment",
        "name": "test_m4i_kubernetes_environment",
        "kubernetesClusters": ["test_m4i_kubernetes_cluster"],
        "description": "something",
    }


path = '/lin_api/kubernetes/kubernetes_environment/'
entity_qn = "testing_m4i_kubernetes_environment"
entity_type = "m4i_kubernetes_environment"


def test_m4i_kubernetes_environment_model_no_kubernetes_clusters(client, request_to_make, check_made, cleanup):
    request_no_kubernetes_clusters = request_to_make.copy()
    request_no_kubernetes_clusters.pop('kubernetesClusters')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kubernetes_clusters)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kubernetesClusters": "'kubernetesClusters' is a required property"}


# END test_m4i_kubernetes_environment_model_no_description


def test_m4i_kubernetes_environment_model_empty_kubernetes_cluster(client, request_to_make, check_made, cleanup):
    request_empty_kubernetes_cluster = request_to_make.copy()
    request_empty_kubernetes_cluster['kubernetesClusters'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_kubernetes_cluster)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 0, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kubernetes_environment_model_empty_kubernetes_cluster
