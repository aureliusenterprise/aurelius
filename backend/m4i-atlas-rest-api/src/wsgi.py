from m4i_atlas_core import ConfigStore
from m4i_compare import app as compare
from m4i_consistency_metrics import app as consistency_metrics
from m4i_data2model import app as data2model
from m4i_data_governance_dashboard import app as data_governance_dashboard
from m4i_lineage_model import app as lineage_model
from m4i_logging_to_elastic import app as elastic_logging
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from m4i_lineage_rest_api.app import register_get_app

from m4i_atlas_config import config
from m4i_elastic_config import config as elastic_config
from flask import Flask
import os

store = ConfigStore.get_instance()
store.load(config)
store.load(elastic_config)

app = Flask("api")

NAMESPACE = os.environ.get('NAMESPACE', '')
if len(NAMESPACE)>0:
    NAMESPACE = '/' + NAMESPACE

RESTAPI_ADDITIONAL_CONTEXT = os.environ.get('RESTAPI_ADDITIONAL_CONTEXT', '')
if len(RESTAPI_ADDITIONAL_CONTEXT)>0:
    RESTAPI_ADDITIONAL_CONTEXT = '/' + RESTAPI_ADDITIONAL_CONTEXT
    
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/data2model": data2model,
    #f"{NAMESPACE}{RESTAPI_ADDITIONAL_CONTEXT}/consistency_metrics": consistency_metrics,
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/compare": compare,
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/lineage_model": lineage_model,
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/data_governance": data_governance_dashboard,
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/logging": elastic_logging,
    NAMESPACE+RESTAPI_ADDITIONAL_CONTEXT+"/lineage": register_get_app()
})

