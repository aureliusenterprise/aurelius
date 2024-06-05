import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_elastic_cluster",
        "replica_count": 1,
        "shard_count": 2
    }


path = '/lin_api/entity/elasticCluster_entity/'
entity_qn = "testing_m4i_elastic_cluster"
entity_type = "m4i_elastic_cluster"


def test_m4i_confluent_cloud_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_confluent_cloud_model_no_name

def test_m4i_confluent_cloud_model_no_replica_count(client, request_to_make):
    request_no_replica_count = request_to_make.copy()
    request_no_replica_count.pop('replica_count')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_replica_count)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "replica_count": "'replica_count' is a required property"}


# END test_m4i_confluent_cloud_model_no_replica_count

def test_m4i_confluent_cloud_model_no_shard_count(client, request_to_make):
    request_no_shard_count = request_to_make.copy()
    request_no_shard_count.pop('shard_count')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_shard_count)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "shard_count": "'shard_count' is a required property"}

# END test_m4i_confluent_cloud_model_no_elasticCluster
