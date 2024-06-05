import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "test_m4i_generic_process",
        "name": "test_m4i_generic_process",
        "processOwner": "test_m4i_person",
        "description": "something",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "source": [
            "test_m4i_source"
        ]
    }


path = '/lin_api/process/generic_process/'
entity_qn = "test_m4i_generic_process"
entity_type = "m4i_generic_process"


def test_m4i_generic_process_model_no_qualifiedName(client, request_to_make):
    request_no_qualifiedName = request_to_make.copy()
    request_no_qualifiedName.pop('qualifiedName')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_qualifiedName)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "qualifiedName": "'qualifiedName' is a required property"}


# END test_m4i_generic_process_model_no_qualifiedName

def test_m4i_generic_process_model_no_name(client, request_to_make, check_made, cleanup):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_generic_process_model_no_name

def test_m4i_generic_process_model_no_processOwner(client, request_to_make, check_made, cleanup):
    request_no_processOwner = request_to_make.copy()
    request_no_processOwner.pop('processOwner')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_processOwner)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_generic_process_model_no_processOwner

def test_m4i_generic_process_model_no_inputs(client, request_to_make):
    request_no_inputs = request_to_make.copy()
    request_no_inputs.pop('inputs')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_inputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "inputs": "'inputs' is a required property"}


# END test_m4i_generic_process_model_no_inputs

def test_m4i_generic_process_model_empty_inputs(client, request_to_make):
    request_empty_inputs = request_to_make.copy()
    request_empty_inputs['inputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_inputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {"inputs": "[] is too short"}


# END test_m4i_generic_process_model_no_inputs

def test_m4i_generic_process_model_no_outputs(client, request_to_make):
    request_no_outputs = request_to_make.copy()
    request_no_outputs.pop('outputs')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_outputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "outputs": "'outputs' is a required property"}


# END test_m4i_generic_process_model_no_outputs

def test_m4i_generic_process_model_empty_outputs(client, request_to_make):
    request_empty_outputs = request_to_make.copy()
    request_empty_outputs['outputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_outputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {"outputs": "[] is too short"}


# END test_m4i_generic_process_model_empty_outputs

def test_m4i_generic_process_model_no_description(client, request_to_make, check_made, cleanup):
    request_no_description = request_to_make.copy()
    request_no_description.pop('description')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_description)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 3, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_generic_process_model_no_description

def test_m4i_generic_process_model_no_source(client, request_to_make, check_made, cleanup):
    request_no_source = request_to_make.copy()
    request_no_source.pop('source')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_source)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_generic_process_model_no_source

def test_m4i_generic_process_model_empty_source(client, request_to_make):
    request_empty_source = request_to_make.copy()
    request_empty_source['source'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_source)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {"source": "[] is too short"}

# END test_m4i_generic_process_model_empty_source
