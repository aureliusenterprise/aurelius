import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_elastic_index",
        "qualifiedName": "testing_elastic_index",
        "cluster": "test_elastic_cluster",
        "environment": "test_elastic_environment",
        "indexTemplate": {
            "mappings": {
                "_meta": {
                    "testing_elastic_field_1": "test_m4i_data_attribute",
                    "testing_elastic_field_2": "test_m4i_data_attribute"
                },
                "properties": {
                    "testing_elastic_field_1": {
                        "type": "keyword"
                    },
                    "testing_elastic_field_2": {
                        "type": "text"
                    }
                }
            }
        }
    }


path = '/lin_api/entity/elasticIndex_entity/'
entity_qn = "testing_elastic_index"
entity_type = "m4i_elastic_index"
fields_qn = [
    "testing_elastic_index--testing_elastic_field_1",
    "testing_elastic_index--testing_elastic_field_2"
]
collection_qn = "test_elastic_environment--test_elastic_cluster--data"


def test_m4i_elasticIndex_entity_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_elasticIndex_entity_model_no_name

def test_m4i_elasticIndex_entity_model_no_cluster(client, request_to_make):
    request_no_cluster = request_to_make.copy()
    request_no_cluster.pop('cluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "cluster": "'cluster' is a required property"}


# END test_m4i_elasticIndex_entity_model_no_cluster


def test_m4i_elasticIndex_entity_model_no_qualifiedName(client, request_to_make):
    request_no_qualifiedName = request_to_make.copy()
    request_no_qualifiedName.pop('qualifiedName')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_qualifiedName)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "qualifiedName": "'qualifiedName' is a required property"}


# END test_m4i_elasticIndex_entity_model_no_qualifiedName


def test_m4i_elasticIndex_entity_model_no_environment(client, request_to_make):
    request_no_environment = request_to_make.copy()
    request_no_environment.pop('environment')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_environment)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "environment": "'environment' is a required property"}


# END test_m4i_elasticIndex_entity_model_no_environment

def test_m4i_elasticIndex_entity_model_no_indexTemplate(client, request_to_make):
    request_no_indexTemplate = request_to_make.copy()
    request_no_indexTemplate.pop('indexTemplate')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_indexTemplate)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "indexTemplate": "'indexTemplate' is a required property"}

# END test_m4i_elasticIndex_entity_model_no_indexTemplate
