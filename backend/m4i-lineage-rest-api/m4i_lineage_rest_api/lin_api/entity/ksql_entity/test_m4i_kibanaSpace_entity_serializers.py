import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_ksql",
        "env": "env",
        "cluster": "cluster",
        "kafka_topic": "test_m4i_kafka_topic",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }


path = '/lin_api/entity/ksql_entity/'
entity_qn = "env--cluster--testing_m4i_ksql"
entity_type = "m4i_ksql"


def test_m4i_ksql_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_ksql_model_no_name

def test_m4i_ksql_model_no_env(client, request_to_make):
    request_no_env = request_to_make.copy()
    request_no_env.pop('env')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_env)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "env": "'env' is a required property"}


# END test_m4i_ksql_model_no_env

def test_m4i_ksql_model_no_cluster(client, request_to_make):
    request_no_cluster = request_to_make.copy()
    request_no_cluster.pop('cluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "cluster": "'cluster' is a required property"}


# END test_m4i_ksql_model_no_cluster

def test_m4i_ksql_model_no_kafka_topic(client, request_to_make):
    request_no_kafka_topic = request_to_make.copy()
    request_no_kafka_topic.pop('kafka_topic')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kafka_topic)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kafka_topic": "'kafka_topic' is a required property"}


# END test_m4i_ksql_model_no_kafka_topic

def test_m4i_ksql_model_no_value_format(client, request_to_make):
    request_no_value_format = request_to_make.copy()
    request_no_value_format.pop('value_format')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_value_format)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "value_format": "'value_format' is a required property"}


# END test_m4i_ksql_model_no_value_format

def test_m4i_ksql_model_no_query(client, request_to_make):
    request_no_query = request_to_make.copy()
    request_no_query.pop('query')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_query)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "query": "'query' is a required property"}


# END test_m4i_ksql_model_no_query

def test_m4i_ksql_model_no_properties(client, request_to_make):
    request_no_properties = request_to_make.copy()
    request_no_properties.pop('properties')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_properties)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "properties": "'properties' is a required property"}

# END test_m4i_ksql_model_no_properties
