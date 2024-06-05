import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_kafka_cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "test_m4i_confluent_environment",
    }


path = '/lin_api/entity/kafkaCluster_entity/'
entity_qn = "test_m4i_confluent_environment--testing_m4i_kafka_cluster"
entity_type = "m4i_kafka_cluster"


def test_m4i_kafka_cluster_model_no_kafka_replicas(client, request_to_make):
    request_no_kafka_replicas = request_to_make.copy()
    request_no_kafka_replicas.pop('kafka_replicas')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kafka_replicas)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kafka_replicas": "'kafka_replicas' is a required property"}


# END test_m4i_kafka_cluster_model_no_kafka_replicas

def test_m4i_kafka_cluster_model_no_kafka_partitions(client, request_to_make):
    request_no_kafka_partitions = request_to_make.copy()
    request_no_kafka_partitions.pop('kafka_partitions')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kafka_partitions)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kafka_partitions": "'kafka_partitions' is a required property"}


# END test_m4i_kafka_cluster_model_no_kafka_partitions

def test_m4i_kafka_cluster_model_no_confluent_environment(client, request_to_make):
    request_no_confluent_environment = request_to_make.copy()
    request_no_confluent_environment.pop('confluent_environment')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_confluent_environment)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "confluent_environment": "'confluent_environment' is a required property"}


# END test_m4i_kafka_cluster_model_no_confluent_environment


def test_m4i_kafka_cluster_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}

# END test_m4i_kafka_cluster_model_no_name
