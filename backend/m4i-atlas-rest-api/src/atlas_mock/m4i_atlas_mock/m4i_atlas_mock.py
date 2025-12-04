import json

from flask import Flask, request

app = Flask(__name__)

data_filtered = {
    "approximateCount": 5,
    "filterValues": {
        "1234": {
            "option": "m4i_data_domain",
            "valueGuid": "1234",
            "valueName": "Finance",
            "valueCount": "3"
        },
        "3232": {
            "option": "m4i_data_domain",
            "valueGuid": "3232",
            "valueName": "HR",
            "valueCount": "2"
        },
        "9874": {
            "option": "m4i_data_entity",
            "valueGuid": "9874",
            "valueName": "Organization",
            "valueCount": "5"
        }
    },
    "entities": [
        {
            "guid": "74cba303-5fe0-495d-adf5-a9f4f28714c3",
            "name": "Agency"
        }
    ]
}

data_unfiltered = {
    "approximateCount": 5,
    "filterValues": {
        "1234": {
            "option": "m4i_data_domain",
            "valueGuid": "1234",
            "valueName": "Finance",
            "valueCount": "3"
        },
        "3232": {
            "option": "m4i_data_domain",
            "valueGuid": "3232",
            "valueName": "HR",
            "valueCount": "2"
        },
        "3445": {
            "option": "m4i_data_domain",
            "valueGuid": "3445",
            "valueName": "Job",
            "valueCount": "1"
        },
        "9874": {
            "option": "m4i_data_entity",
            "valueGuid": "9874",
            "valueName": "Organization",
            "valueCount": "5"
        },
        "9828": {
            "option": "m4i_system",
            "valueGuid": "9828",
            "valueName": "eudtc1-ebsp-db1.vanoord.org",
            "valueCount": "4"
        }
    },
    "entities": [
        {
            "guid": "74cba303-5fe0-495d-adf5-a9f4f28714c3",
            "name": "Agency"
        }, {
            "guid": "5acd3a39-b63c-4994-81f1-e253733aaa31",
            "name": "Finance and Control"
        }, {
            "guid": "24de1b85-0430-4800-ad52-f40a5956aec8",
            "name": "PayRoll"
        },
        {
            "guid": "f51b6015-777e-4078-be57-89cb902f3d36",
            "name": "Albert-Jan Kroezen"
        },
        {
            "guid": "d1ae1726-f49c-4f1e-9e0b-8de7a6561509",
            "name": "test m4i_kafka_topic"
        }
    ]
}


@app.route('/', methods=['POST'])
def mock_response():

    params = request.get_json()

    is_filtered = "m4i_data_domain" in params and "1234" in params["m4i_data_domain"]
    
    data = data_filtered if is_filtered else data_unfiltered

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    return response
