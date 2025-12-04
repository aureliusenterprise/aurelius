from asyncio import run

from flask import Flask, Response
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared

from ..core.source import get_data_domains

app = Flask(__name__)

register_shared(app)


@app.route('/dashboard', methods=['GET'])
@requires_auth(transparent=True)
def dashboard(access_token=None):
    resp = run(get_data_domains(access_token=access_token))
    return Response(resp.to_json(), 200)
# END dashboard
