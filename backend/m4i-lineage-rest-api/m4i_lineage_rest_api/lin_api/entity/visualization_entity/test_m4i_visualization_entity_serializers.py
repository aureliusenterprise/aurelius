import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_visualization_entity",
        "name": "testing_m4i_visualization_entity",
        "description": "something",
        "updatedAt": "Updated At",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "test_m4i_dashboard"
        ],
        "childDataset": [
            "test_m4i_indexPattern"
        ],
        "type": "a type",
        "visualizationType": "visualization type"
    }


path = '/lin_api/entity/visualization_entity/'
entity_qn = "testing_m4i_visualization_entity"
entity_type = "m4i_visualization"


def test_m4i_visualization_model_no_updatedAt(client, request_to_make):
    request_no_updatedAt = request_to_make.copy()
    request_no_updatedAt.pop('updatedAt')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_updatedAt)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "updatedAt": "'updatedAt' is a required property"}


# END test_m4i_visualization_model_no_updatedAt

def test_m4i_visualization_model_no_version(client, request_to_make):
    request_no_version = request_to_make.copy()
    request_no_version.pop('version')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_version)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "version": "'version' is a required property"}


# END test_m4i_visualization_model_no_version

def test_m4i_visualization_model_no_type(client, request_to_make):
    request_no_type = request_to_make.copy()
    request_no_type.pop('type')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_type)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "type": "'type' is a required property"}


# END test_m4i_visualization_model_no_type

def test_m4i_visualization_model_no_creator(client, request_to_make, check_made, cleanup):
    request_no_creator = request_to_make.copy()
    request_no_creator.pop('creator')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_creator)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_visualization_model_no_creator

def test_m4i_visualization_model_no_parentDataset(client, request_to_make, check_made, cleanup):
    request_no_parentDataset = request_to_make.copy()
    request_no_parentDataset.pop('parentDataset')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_parentDataset)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_visualization_model_no_parentDataset

def test_m4i_visualization_model_no_childDataset(client, request_to_make, check_made, cleanup):
    request_no_childDataset = request_to_make.copy()
    request_no_childDataset.pop('childDataset')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_childDataset)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "childDataset": "'childDataset' is a required property"}


# END test_m4i_visualization_model_no_childDataset

def test_m4i_visualization_model_no_visualizationType(client, request_to_make, check_made, cleanup):
    request_no_visualizationType = request_to_make.copy()
    request_no_visualizationType.pop('visualizationType')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_visualizationType)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 3, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_visualization_model_no_visualizationType
