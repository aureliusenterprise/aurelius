import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_index_pattern",
        "name": "testing_m4i_index_pattern",
        "description": "something",
        "indexPattern": "pattern",
        "updatedAt": "updated at",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "test_m4i_visualization"
        ]
    }


path = '/lin_api/entity/indexPattern_entity/'
entity_qn = "testing_m4i_index_pattern"
entity_type = "m4i_index_pattern"


def test_m4i_index_pattern_model_no_updatedAt(client, request_to_make):
    request_no_updatedAt = request_to_make.copy()
    request_no_updatedAt.pop('updatedAt')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_updatedAt)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "updatedAt": "'updatedAt' is a required property"}


# END test_m4i_index_pattern_model_no_updatedAt

def test_m4i_index_pattern_model_no_version(client, request_to_make):
    request_no_version = request_to_make.copy()
    request_no_version.pop('version')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_version)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "version": "'version' is a required property"}


# END test_m4i_index_pattern_model_no_version

def test_m4i_index_pattern_model_no_indexPattern(client, request_to_make):
    request_no_indexPattern = request_to_make.copy()
    request_no_indexPattern.pop('indexPattern')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_indexPattern)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "indexPattern": "'indexPattern' is a required property"}


# END test_m4i_index_pattern_model_no_indexPattern

def test_m4i_index_pattern_model_no_creator(client, request_to_make, check_made, cleanup):
    request_no_creator = request_to_make.copy()
    request_no_creator.pop('creator')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_creator)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_index_pattern_model_no_creator

def test_m4i_index_pattern_model_no_parentDataset(client, request_to_make, check_made, cleanup):
    request_no_parentDataset = request_to_make.copy()
    request_no_parentDataset.pop('parentDataset')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_parentDataset)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_index_pattern_model_no_parentDataset
