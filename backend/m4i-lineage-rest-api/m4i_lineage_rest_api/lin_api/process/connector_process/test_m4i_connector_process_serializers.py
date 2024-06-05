import pytest


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "test_m4i_connector_process",
        "name": "test_m4i_connector_process",
        "description": "test_m4i_connector_process",
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
        "connectorType": "test_m4i_connector_process Type",
        "server": "test_m4i_connector_process Server"
    }


path = '/lin_api/process/connector_process/'
entity_qn = "test_m4i_connector_process"
entity_type = "m4i_connector_process"


def test_m4i_connector_process_model_no_connectorType(client, request_to_make):
    request_no_connectorType = request_to_make.copy()
    request_no_connectorType.pop('connectorType')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_connectorType)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "connectorType": "'connectorType' is a required property"}


# END test_m4i_connector_process_model_no_connectorType


def test_m4i_connector_process_model_no_server(client, request_to_make):
    request_no_server = request_to_make.copy()
    request_no_server.pop('server')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_server)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "server": "'server' is a required property"}

# END test_m4i_connector_process_model_no_server
