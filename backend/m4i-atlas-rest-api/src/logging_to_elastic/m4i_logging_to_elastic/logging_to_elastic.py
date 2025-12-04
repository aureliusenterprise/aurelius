import json
from elasticsearch import Elasticsearch
from flask import Flask, request
from m4i_atlas_core import ConfigStore
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared

app = Flask(__name__)

store = ConfigStore.get_instance()
register_shared(app)

def write_to_elastic(index_name: str, message: dict):
    username, password, url_with_port, elastic_ca_certs_path = store.get_many('elastic_username', 'elastic_password',
                                                                              'elastic_host', 'elastic_ca_certs_path')
    if elastic_ca_certs_path == None:
        connection = Elasticsearch(
            url_with_port,
            basic_auth=(username, password),
        )
    else:
        connection = Elasticsearch(
            url_with_port,
            basic_auth=(username, password),
            ca_certs=elastic_ca_certs_path
        )

    response = connection.index(index=index_name, document=message)
    return response


@app.route('/log', methods=['POST'])
@requires_auth(transparent=True)
def logging_to_elastic(access_token=None):
    """
    This is the endpoint /log which is used to push logs (body of the request) to elastic index "atlas-logging".
    For the frontend the path will be /repository/api/log.

    :param access_token: the bearer token of the frontend used to verify where this request is coming from.
    :return: Empty response
    """
    index_name: str = 'atlas-logging'
    message = request.get_json(force=True)
    write_to_elastic(index_name, message)
    return '', 204


# END logging_to_elastic

@app.route('/error', methods=['POST'])
@requires_auth(transparent=True)
def errors_to_elastic(access_token=None):
    """
    This is the endpoint /error which is used to push reported errors (body of the request) to elastic index "atlas-error".
    For the frontend the path will be /repository/api/error.

    :param access_token: the bearer token of the frontend used to verify where this request is coming from.
    :return: Empty response
    """
    index_name: str = 'atlas-error'
    message = request.get_json(force=True)
    message['state'] = json.dumps(message['state']) # this is turned into a string because the number of fields are too high for elastic to parse and index. This way we still get to keep the data but it is not searchable
    write_to_elastic(index_name,  message)

    return '', 204

# END errors_to_elastic