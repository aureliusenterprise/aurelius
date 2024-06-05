import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_kafka_topic",
        "cluster": "test_m4i_kafka_cluster",
        "environment": "test_m4i_confluent_environment",
        "partitions": 3,
        "replicas": 2,
        "key_schema": "string",
        "value_schema": {
            "fields": [
                {
                    "name": "testing_kafka_field_1",
                    "doc": "test_m4i_data_attribute",
                    "type": "string"
                },
                {
                    "name": "testing_kafka_field_2",
                    "doc": None,
                    "type": [
                        "null",
                        {
                            "fields": [
                                {
                                    "name": "testing_kafka_field_3",
                                    "doc": "test_m4i_data_attribute",
                                    "type": "string"
                                }
                            ],
                            "name": "testing_kafka_field_2",
                            "doc": "test_m4i_data_attribute",
                            "type": "record"
                        }
                    ]
                }
            ],
            "name": "testing_m4i_kafka_topic__value",
            "doc": None,
            "namespace": "namespace",
            "type": "record"
        }
    }


path = '/lin_api/entity/kafkaTopic_entity/'
entity_qn = "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
entity_type = "m4i_kafka_topic"
fields_qn = [
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_1",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2--testing_kafka_field_2",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2--testing_kafka_field_2--testing_kafka_field_3"
]
collection_qn = "test_m4i_confluent_environment--test_m4i_kafka_cluster--data"


def test_m4i_kafkaTopic_entity_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_name

def test_m4i_kafkaTopic_entity_model_no_cluster(client, request_to_make):
    request_no_cluster = request_to_make.copy()
    request_no_cluster.pop('cluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "cluster": "'cluster' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_cluster


def test_m4i_kafkaTopic_entity_model_no_partitions(client, request_to_make):
    request_no_partitions = request_to_make.copy()
    request_no_partitions.pop('partitions')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_partitions)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "partitions": "'partitions' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_partitions

def test_m4i_kafkaTopic_entity_model_string_partitions(client, request_to_make):
    request_string_partitions = request_to_make.copy()
    request_string_partitions['partitions'] = '3'

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_string_partitions)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "partitions": "'3' is not of type 'integer'"}


# END test_m4i_kafkaTopic_entity_model_string_partitions

def test_m4i_kafkaTopic_entity_model_no_replicas(client, request_to_make):
    request_no_replicas = request_to_make.copy()
    request_no_replicas.pop('replicas')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_replicas)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "replicas": "'replicas' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_replicas

def test_m4i_kafkaTopic_entity_model_string_replicas(client, request_to_make):
    request_string_replicas = request_to_make.copy()
    request_string_replicas['replicas'] = '3'

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_string_replicas)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "replicas": "'3' is not of type 'integer'"}


# END test_m4i_kafkaTopic_entity_model_string_replicas

def test_m4i_kafkaTopic_entity_model_no_key_schema(client, request_to_make):
    request_no_key_schema = request_to_make.copy()
    request_no_key_schema.pop('key_schema')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_key_schema)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "key_schema": "'key_schema' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_key_schema

def test_m4i_kafkaTopic_entity_model_no_value_schema(client, request_to_make):
    request_no_value_schema = request_to_make.copy()
    request_no_value_schema.pop('value_schema')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_value_schema)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "value_schema": "'value_schema' is a required property"}


# END test_m4i_kafkaTopic_entity_model_no_value_schema

def test_m4i_kafkaTopic_entity_model_empty_value_schema(client, request_to_make):
    request_empty_value_schema = request_to_make.copy()
    request_empty_value_schema['value_schema'] = {}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_value_schema)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {'value_schema': '{} is not valid under any of the given schemas'}


# END test_m4i_kafkaTopic_entity_model_no_value_schema


def test_m4i_kafkaTopic_entity_model_value_schema_no_name(client, request_to_make):
    request_value_schema_no_name = request_to_make.copy()
    request_value_schema_no_name['value_schema'] = {'fields': [],
                                                    'doc': "doc_field",
                                                    'type': "a type"}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {'value_schema': "{'doc': 'doc_field', 'fields': [], 'type': 'a type'} is not "
                                                'valid under any of the given schemas'}


# END test_m4i_kafkaTopic_entity_model_value_schema_no_name

def test_m4i_kafkaTopic_entity_model_value_schema_no_doc(client, request_to_make):
    request_value_schema_no_doc = request_to_make.copy()
    request_value_schema_no_doc['value_schema'] = {
        'fields': [],
        'name': "some Name",
        'type': "a type"}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_no_doc)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {'value_schema': "{'fields': [], 'name': 'some Name', 'type': 'a type'} is not "
                                                'valid under any of the given schemas'}


# END test_m4i_kafkaTopic_entity_model_value_schema_no_doc

def test_m4i_kafkaTopic_entity_model_value_schema_null_doc(client, cleanup, check_made, request_to_make):
    request_value_schema_null_doc = request_to_make.copy()
    request_value_schema_null_doc['value_schema'] = {
        'fields': [],
        'doc': None,
        'name': "some Name",
        'type': "string"}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_null_doc)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 2, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
    guid = asyncio.run(check_made(entity_qn=collection_qn, entity_type="m4i_collection"))
    asyncio.run(cleanup(guid=guid, entity_qn=collection_qn, entity_type="m4i_collection"))


# END test_m4i_kafkaTopic_entity_model_value_schema_null_doc

def test_m4i_kafkaTopic_entity_model_value_schema_no_type(client, request_to_make):
    request_value_schema_no_type = request_to_make.copy()
    request_value_schema_no_type['value_schema'] = {
        'fields': [],
        'name': "some Name",
        'doc': "doc_field"}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_no_type)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {'value_schema': "{'doc': 'doc_field', 'fields': [], 'name': 'some Name'} is "
                                                'not valid under any of the given schemas'}


# END test_m4i_kafkaTopic_entity_model_value_schema_no_type

def test_m4i_kafkaTopic_entity_model_value_schema_no_fields(client, request_to_make):
    request_value_schema_no_fields = request_to_make.copy()
    request_value_schema_no_fields['value_schema'] = {
        'name': "some Name",
        'doc': "doc_field",
        'type': "a type"}

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_no_fields)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {'value_schema': "{'doc': 'doc_field', 'name': 'some Name', 'type': 'a type'} "
                                                'is not valid under any of the given schemas'}


# END test_m4i_kafkaTopic_entity_model_value_schema_no_fields


def test_m4i_kafkaTopic_entity_model_value_schema_string(client, cleanup, check_made, request_to_make):
    request_value_schema_string = request_to_make.copy()
    request_value_schema_string['value_schema'] = "string"

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_value_schema_string)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 2, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
    guid = asyncio.run(check_made(entity_qn=collection_qn, entity_type="m4i_collection"))
    asyncio.run(cleanup(guid=guid, entity_qn=collection_qn, entity_type="m4i_collection"))
