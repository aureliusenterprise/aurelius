import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_confluent_cloud"
    }


path = '/lin_api/entity/confluentCloud_entity/'
entity_qn = "testing_m4i_confluent_cloud"
entity_type = "m4i_confluent_cloud"


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
