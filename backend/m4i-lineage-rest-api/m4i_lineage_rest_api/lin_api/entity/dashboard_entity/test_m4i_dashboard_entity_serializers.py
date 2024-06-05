import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_dashboard_entity",
        "name": "testing_m4i_dashboard_entity",
        "description": "asda",
        "updatedAt": "updatedAT",
        "version": "VERSION",
        "kibanaSpace": "test_m4i_kibana_space",
        "creator": [
            "test_m4i_person"
        ],
        "child_dataset": [
            "test_m4i_visualization"
        ]
    }


path = '/lin_api/entity/dashboard_entity/'
entity_qn = "testing_m4i_dashboard_entity"
entity_type = "m4i_dashboard"


def test_m4i_dashboard_model_no_updatedAt(client, request_to_make):
    request_no_updatedAt = request_to_make.copy()
    request_no_updatedAt.pop('updatedAt')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_updatedAt)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "updatedAt": "'updatedAt' is a required property"}


# END test_m4i_dashboard_model_no_updatedAt

def test_m4i_dashboard_model_no_version(client, request_to_make):
    request_no_version = request_to_make.copy()
    request_no_version.pop('version')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_version)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "version": "'version' is a required property"}


# END test_m4i_dashboard_model_no_version

def test_m4i_dashboard_model_no_kibanaSpace(client, request_to_make):
    request_no_kibanaSpace = request_to_make.copy()
    request_no_kibanaSpace.pop('kibanaSpace')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_kibanaSpace)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "kibanaSpace": "'kibanaSpace' is a required property"}


# END test_m4i_dashboard_model_no_kibanaSpace
def test_m4i_dashboard_model_no_child_dataset(client, request_to_make):
    request_no_child_dataset = request_to_make.copy()
    request_no_child_dataset.pop('child_dataset')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_child_dataset)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "child_dataset": "'child_dataset' is a required property"}


# END test_m4i_dashboard_model_no_child_dataset
def test_m4i_dashboard_model_no_creator(client, request_to_make, check_made, cleanup):
    request_no_creator = request_to_make.copy()
    request_no_creator.pop('creator')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_creator)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_dashboard_model_no_creator
