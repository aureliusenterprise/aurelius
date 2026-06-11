import asyncio
from json import dumps
from typing import Any, Dict, Optional

from flask import Flask, abort, request
from requests_cache import install_cache  # type: ignore[import-untyped]

from m4i_analytics.m4i.platform.PlatformApi import PlatformApi
from m4i_backend_core.auth import requires_auth  # type: ignore[import-untyped]
from m4i_backend_core.shared import register as register_shared

from .report import calculate_metric, generate_metric
from .report import report as report_structure

app = Flask(__name__)

# Register the shared core module with the application
register_shared(app)

# Enable chache-ing for GET requests. This helps load models faster on repeated requests.
CACHE_NAME = "consistency_metrics"
EXPIRE_AFTER = 60 * 60 * 24  # seconds = 1 day
CACHED_PATHS = ["private/metric", "model/retrieve"]
install_cache(
    CACHE_NAME,
    backend="sqlite",
    expire_after=EXPIRE_AFTER,
    filter_fn=lambda response: any(path in response.url for path in CACHED_PATHS),  # type: ignore[arg-type]
)


# Application routes
# This is the entry route for the front end. Can be used to retrieve metrics and metric categories.
@app.route("/metric", methods=["GET"])
@requires_auth
def metric(access_token: Optional[str] = None):
    model_options = {
        "fullProjectName": request.args.get("project"),
        "branchName": request.args.get("branch"),
        "version": int(request.args.get("version") or "1"),
        "userid": "consistency_metrics",
        "access_token": access_token,
    }

    # Retrieve the role of the user in the given project.
    # If this fails for whatever reason, abort with a 403 (forbidden) status.
    try:
        PlatformApi.get_user_role(  # type: ignore[call-arg]
            request.args.get("project") or "", access_token=access_token
        )
    except Exception:
        abort(403)
    # END TRY

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    metric_future = generate_metric(metric_key=request.args.get("metric") or "", model_options=model_options)

    metric: Dict[str, Any] = loop.run_until_complete(metric_future)

    loop.close()

    # Ensure keys are not sorted to preserve the report structure
    return dumps(metric, sort_keys=False)


# END metric


# Internal route used by the app for caching of metrics. Can be used to retrieve metrics ONLY.
@app.route("/private/metric", methods=["GET"])
@requires_auth
def private_metric(access_token: Optional[str] = None):
    model_options = {
        "fullProjectName": request.args.get("project"),
        "branchName": request.args.get("branch"),
        "version": int(request.args.get("version") or "1"),
        "userid": "consistency_metrics",
        "access_token": access_token,
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    metric_future = calculate_metric(metric_key=request.args.get("metric") or "", model_options=model_options)

    metric: Dict[str, Any] = loop.run_until_complete(metric_future)

    loop.close()

    # Ensure keys are not sorted to preserve the report structure
    return dumps(metric, sort_keys=False)


# END private_metric


@app.route("/report", methods=["GET"])
def report():
    return dumps(report_structure, sort_keys=False)


# END report
