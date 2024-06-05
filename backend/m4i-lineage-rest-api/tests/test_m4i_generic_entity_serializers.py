import pytest

from m4i_atlas_core import ConfigStore
# from m4i_lineage_rest_api import get_atlas_connection
from m4i_lineage_rest_api.app import flask_app
from .test_settings import atlas_sets


def config():
    store = ConfigStore.get_instance()
    store.set("atlas.server.url", atlas_sets['server'])
    store.set("atlas.server.port", atlas_sets['port'])
    store.set("atlas.server.username", atlas_sets['username'])
    store.set("atlas.server.password", atlas_sets['password'])


# END config


config()
# atlas_test = get_atlas_connection()


@pytest.fixture
def client():
    app_flask = flask_app()
    app_flask.initialize_app()
    app_flask.app.config['TESTING'] = True
    with app_flask.app.test_client() as client:
        yield client
    # END client


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "test_m4i_visualization_entity",
        "name": "test_m4i_visualization_entity",
        "description": "something",
        "updatedAt": "Updated At",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "tester_m4i_dashboard"
        ],
        "childDataset": [
            "tester_m4i_indexPattern"
        ],
        "type": "a type",
        "visualizationType": "visualization type"
    }


path = '/lin_api/entity/visualization_entity/'


def test_m4i_visualization_entity_model_no_name(client, request_to_make):
    request_no_name = request_to_make.copy()
    request_no_name.pop('name')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_name)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "name": "'name' is a required property"}

# END test_m4i_visualization_entity_model_no_name


def test_m4i_visualization_entity_model_no_version(client, request_to_make):
    request_no_qualifiedName = request_to_make.copy()
    request_no_qualifiedName.pop('qualifiedName')

    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_no_qualifiedName)
    assert t.status_code == 400
    t_json = t.get_json()
    assert t_json['message'] == "Input payload validation failed"
    assert t_json['errors'] == {
        "qualifiedName": "'qualifiedName' is a required property"}

# END test_m4i_visualization_entity_model_no_qualifiedName
