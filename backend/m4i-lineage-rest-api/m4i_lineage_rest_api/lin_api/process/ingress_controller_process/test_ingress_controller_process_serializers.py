import asyncio

import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_ingress_controller_process",
        "name": "testing_m4i_ingress_controller_process",
        "description": "test_m4i_ingress_controller_process",
        "processOwner": "test_m4i_person",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "ingressObject": [
            "test_m4i_ingress_object_process"
        ],
        "cluster": "test_m4i_kubernetes_cluster"
    }


path = '/lin_api/process/ingress_controller_process/'
entity_qn = "testing_m4i_ingress_controller_process"
entity_type = "m4i_ingress_controller_process"


def test_m4i_ingress_controller_process_model_no_cluster(client, request_to_make):
    request_no_cluster = request_to_make.copy()
    request_no_cluster.pop('cluster')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_cluster)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "cluster": "'cluster' is a required property"}


# END test_m4i_ingress_controller_process_model_no_cluster

def test_m4i_ingress_controller_process_model_no_inputs(client, request_to_make):
    request_no_inputs = request_to_make.copy()
    request_no_inputs.pop('inputs')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_inputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "inputs": "'inputs' is a required property"}


# END test_m4i_ingress_controller_process_model_no_inputs

def test_m4i_ingress_controller_process_model_no_outputs(client, request_to_make):
    request_no_outputs = request_to_make.copy()
    request_no_outputs.pop('outputs')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_outputs)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "outputs": "'outputs' is a required property"}


# END test_m4i_ingress_controller_process_model_no_outputs

def test_m4i_ingress_controller_process_model_no_ingress_object(client, request_to_make):
    request_no_ingress_object = request_to_make.copy()
    request_no_ingress_object.pop('ingressObject')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_ingress_object)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "ingressObject": "'ingressObject' is a required property"}


# END test_m4i_ingress_controller_process_model_no_ingress_object

def test_m4i_ingress_controller_process_model_no_process_owner(client, request_to_make, check_made, cleanup):
    request_no_process_owner = request_to_make.copy()
    request_no_process_owner.pop("processOwner")

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_process_owner)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 3, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_ingress_controller_process_model_no_process_owner

def test_m4i_ingress_controller_process_model_empty_inputs(client, request_to_make, check_made, cleanup):
    request_empty_inputs = request_to_make.copy()
    request_empty_inputs['inputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_inputs)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 4, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_ingress_controller_process_model_empty_inputs

def test_m4i_ingress_controller_process_model_empty_outputs(client, request_to_make, check_made, cleanup):
    request_empty_outputs = request_to_make.copy()
    request_empty_outputs['outputs'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_outputs)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 4, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_m4i_ingress_controller_process_model_empty_outputs

def test_m4i_ingress_controller_process_model_empty_ingress_object(client, request_to_make, check_made, cleanup):
    request_empty_ingress_object = request_to_make.copy()
    request_empty_ingress_object['ingressObject'] = []

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_empty_ingress_object)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 3, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))

# END test_m4i_ingress_controller_process_model_empty_ingress_object
