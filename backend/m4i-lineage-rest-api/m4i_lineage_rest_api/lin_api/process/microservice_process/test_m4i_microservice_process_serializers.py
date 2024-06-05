import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_microservice_process",
        "name": "testing_m4i_microservice_process",
        "description": "test_m4i_microservice_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "source": [
            "test_m4i_source"
        ],
        "system": "test_m4i_kubernetes_pod"
    }


path = '/lin_api/process/microservice_process/'
entity_qn = "testing_m4i_microservice_process"
entity_type = "m4i_microservice_process"


def test_m4i_microservice_process_model_no_system(client, request_to_make):
    request_no_system = request_to_make.copy()
    request_no_system.pop('system')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_system)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "system": "'system' is a required property"}


# END test_m4i_microservice_process_model_no_system


def test_m4i_microservice_process_model_empty_inputs(client, request_to_make, check_made, cleanup):
    request_empty_inputs = request_to_make.copy()
    request_empty_inputs['inputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_inputs)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 4, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_microservice_process_model_empty_inputs

def test_m4i_microservice_process_model_empty_outputs(client, request_to_make, check_made, cleanup):
    request_empty_outputs = request_to_make.copy()
    request_empty_outputs['outputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_outputs)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 4, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_microservice_process_model_empty_outputs
