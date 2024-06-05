import pytest


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_confluent_environment",
        "schema_registry": True,
        "confluent_cloud": "confluent_cloud"
    }


path = '/lin_api/entity/confluentEnvironment_entity/'
entity_qn = "testing_m4i_confluent_environment"
entity_type = "m4i_confluent_environment"


def test_m4i_confluent_environment_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}


# END test_m4i_confluent_environment_model_no_name


def test_m4i_confluent_environment_model_no_confluent_cloud(client, request_to_make):
    request_no_confluent_cloud = request_to_make.copy()
    request_no_confluent_cloud.pop('confluent_cloud')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_confluent_cloud)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "confluent_cloud": "'confluent_cloud' is a required property"}


# END test_m4i_confluent_environment_model_no_confluent_cloud

def test_m4i_confluent_environment_model_no_schema_registry(client, request_to_make):
    request_no_schema_registry = request_to_make.copy()
    request_no_schema_registry.pop('schema_registry')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_schema_registry)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "schema_registry": "'schema_registry' is a required property"}

# END test_m4i_confluent_environment_model_no_schema_registry
