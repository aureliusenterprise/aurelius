import json
from typing import Iterable, Tuple

from flask import Flask, request

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
    ArchimateUtils
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared

from .logic import compare_models

app = Flask(__name__)

# Register the shared core module with the application
register_shared(app)


@app.route('/', methods=['GET'])
@requires_auth
def compare(access_token=None):

    def format_difference(difference: Tuple[str, str]):
        id_, difference_type = difference
        return {
            'id': id_,
            'difference': difference_type
        }
    # END format_differences

    project = request.args.get('project')

    # Structure the request parameters
    base_model_options = {
        'fullProjectName': project,
        'branchName': request.args.get('baseBranch'),
        'version': int(request.args.get('baseVersion')) if 'baseVersion' in request.args else None,
        'userid': 'compare'
    }

    other_model_options = {
        'fullProjectName': project,
        'branchName': request.args.get('otherBranch'),
        'version': int(request.args.get('otherVersion')) if 'otherVersion' in request.args else None,
        'userid': 'compare'
    }

    # Retrieve the two models that should be compared
    base_model = ArchimateUtils.load_model_from_repository(
        **base_model_options,
        access_token=access_token
    )
    other_model = ArchimateUtils.load_model_from_repository(
        **other_model_options,
        access_token=access_token
    )

    # Compare the models
    differences, merged_model = compare_models(base_model, other_model)

    # Turn the differences into objects and serialize them as a JSON list
    difference_objects = map(format_difference, differences)
    differences_json = json.dumps(list(difference_objects))

    # Serialize the model to JSON
    model_json = ArchimateUtils.to_JSON(merged_model)

    return f'{{"model":{model_json}, "differences":{differences_json}}}'
# END compare
