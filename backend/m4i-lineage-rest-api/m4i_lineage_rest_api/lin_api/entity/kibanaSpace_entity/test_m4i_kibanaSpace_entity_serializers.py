import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "definition": "definition",
        "avatar_color": "avatar_color",
        "avatar_initials": "avatar_initials",
        "elastic_cluster": "test_m4i_elastic_cluster",
        "name": "testing_m4i_kibana_space",

    }


path = '/lin_api/entity/kibanaSpace_entity/'
entity_qn = "test_m4i_elastic_cluster--testing_m4i_kibana_space"
entity_type = "m4i_kibana_space"


def test_m4i_kibana_space_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_kibana_space_model_no_name

def test_m4i_kibana_space_model_no_avatar_color(client, request_to_make):
    request_no_avatar_color = request_to_make.copy()
    request_no_avatar_color.pop('avatar_color')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_avatar_color)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "avatar_color": "'avatar_color' is a required property"}


# END test_m4i_kibana_space_model_no_avatar_color

def test_m4i_kibana_space_model_no_avatar_initials(client, request_to_make):
    request_no_avatar_initials = request_to_make.copy()
    request_no_avatar_initials.pop('avatar_initials')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_avatar_initials)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "avatar_initials": "'avatar_initials' is a required property"}


# END test_m4i_kibana_space_model_no_avatar_initials

def test_m4i_kibana_space_model_no_elastic_cluster(client, request_to_make):
    request_no_elastic_cluster = request_to_make.copy()
    request_no_elastic_cluster.pop('elastic_cluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_elastic_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "elastic_cluster": "'elastic_cluster' is a required property"}


# END test_m4i_kibana_space_model_no_elastic_cluster

def test_m4i_kibana_space_model_no_definition(client, request_to_make, check_made, cleanup):
    request_no_definition = request_to_make.copy()
    request_no_definition.pop('definition')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_definition)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_kibana_space_model_no_definition
