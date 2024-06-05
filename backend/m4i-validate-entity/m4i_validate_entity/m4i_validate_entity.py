from m4i_backend_core.shared import register as register_shared
from m4i_backend_core.auth import requires_auth
import json

from flask import Flask

app = Flask(__name__)

# Register the shared core module with the application
register_shared(app)

output = {
    "dataEntity": {
        "items": [
            {
                "result": {"raw": "This entity is missing a dataEntity"},
                "dataqualitytype": {"raw": "attribute"},
                "usedattributes": {"raw": ["dataEntity"]},
                "name": {"raw": "Attribute - dataEntity"},
                "compliant": {"raw": "0"},
                "_meta": {
                    "engine": "atlas-dev-gov-quality",
                    "score": 1,
                    "id": "doc-6290d9e0dd895e02b897451f"
                },
                "id": {"raw": "doc-6290d9e0dd895e02b897451f"}
            }
        ],
        "isNonCompliant": True
    },
    "definition": {
        "items": [
            {
                "result": {"raw": "This entity has a definition"},
                "dataqualitytype": {"raw": "attribute"},
                "usedattributes": {"raw": ["definition"]},
                "name": {"raw": "Attribute - definition"},
                "compliant": {"raw": "1"},
                "_meta": {
                    "engine": "atlas-dev-gov-quality",
                    "score": 1,
                    "id": "doc-6290d9dedd895e197b974510"
                },
                "id": {"raw": "doc-6290d9dedd895e197b974510"}
            }
        ],
        "isNonCompliant": False
    },
    "domainLead": {
        "items": [
            {
                "result": {"raw": "This entity is missing a domainLead"},
                "dataqualitytype": {"raw": "attribute"},
                "usedattributes": {"raw": ["domainLead"]},
                "name": {"raw": "Attribute - domainLead"},
                "compliant": {"raw": "0"},
                "_meta": {
                    "engine": "atlas-dev-gov-quality",
                    "score": 1,
                    "id": "doc-6290d9e0dd895e02b8974528"
                },
                "id": {"raw": "doc-6290d9e0dd895e02b8974528"}
            }
        ],
        "isNonCompliant": True
    },
    "name": {
        "items": [
            {
                "result": {"raw": "This entity has a name"},
                "dataqualitytype": {"raw": "attribute"},
                "usedattributes": {"raw": ["name"]},
                "name": {"raw": "Attribute - name"},
                "compliant": {"raw": "1"},
                "_meta": {
                    "engine": "atlas-dev-gov-quality",
                    "score": 1,
                    "id": "doc-6290d9dedd895e197b974507"
                },
                "id": {"raw": "doc-6290d9dedd895e197b974507"}
            }
        ],
        "isNonCompliant": False
    }
}


@app.route('/', methods=['POST'])
@requires_auth(transparent=True)
def mock_response(access_token=None):

    response = app.response_class(
        response=json.dumps(output),
        status=200,
        mimetype='application/json'
    )

    return response
# END mock_response
