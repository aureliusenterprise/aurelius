import logging.config
import os
from flask import Flask, Blueprint
from m4i_atlas_core import ConfigStore, register_atlas_entity_types, \
    data_dictionary_entity_types, kubernetes_entity_types, connectors_entity_types
from m4i_backend_core.shared import register as register_shared

from .config import config
from .credentials import credentials
from m4i_lineage_rest_api import settings
from .lin_api.process.microservice_process.microservice_process import ns as microservice_namespace
from .lin_api.process.generic_process.generic_process import ns as generic_process_namespace
from .lin_api.process.connector_process.connector_process import ns as connector_process_namespace
from .lin_api.restplus import api  ## where exception and error messages are written
from .lin_api.entity.dashboard_entity.Dashboard_Entity import ns as dashboard_entity_namespace
from .lin_api.entity.indexPattern_entity.IndexPattern_Entity import ns as indexPattern_entity_namespace
from .lin_api.entity.visualization_entity.Visualization_Entity import ns as visualization_entity_namespace
from .lin_api.entity.kafkaTopic_entity.KafkaTopic_entity import ns as kafkaTopic_entity_namespace
from .lin_api.entity.elasticIndex_entity.ElasticIndex_entity import ns as elasticIndex_entity_namespace
from .lin_api.entity.confluentEnvironment_entity.ConfluentEnvironment_Entity import \
    ns as confluentEnvironment_entity_namespace
from .lin_api.entity.kafkaCluster_entity.kafkaCluster_Entity import ns as kafkaCluster_entity_namespace
from .lin_api.entity.elasticCluster_entity.elasticCluster_Entity import ns as elasticCluster_entity_namespace
from .lin_api.entity.kibanaSpace_entity.kibanaSpace_Entity import ns as kibanaSpace_entity_namespace
from .lin_api.kubernetes.kubernetes_environment.kubernetes_environment import ns as kubernetes_environment_namespace
from .lin_api.kubernetes.kubernetes_cluster.kubernetes_cluster import ns as kubernetes_cluster_namespace
from .lin_api.kubernetes.kubernetes_namespace.kubernetes_namespace import ns as kubernetes_namespace_namespace
from .lin_api.kubernetes.kubernetes_deployment.kubernetes_deployment import ns as kubernetes_deployment_namespace
from .lin_api.kubernetes.kubernetes_cronjob.kubernetes_cronjob import ns as kubernetes_cronjob_namespace
from .lin_api.kubernetes.kubernetes_pod.kubernetes_pod import ns as kubernetes_pod_namespace
from .lin_api.process.api_operation_process.api_operation_process import ns as api_operation_process_namespace
from .lin_api.process.ingress_controller_process.ingress_controller_process import ns as ingress_controller_process_namespace
from .lin_api.process.ingress_object_process.ingress_object_process import ns as ingress_object_process_namespace
from .lin_api.process.kubernetes_service_process.kubernetes_service_process import ns as kubernetes_service_process_namespace
from .lin_api.entity.confluentCloud_Entity.ConfluentCloud_Entity import ns as confluent_cloud_namespace
from .lin_api.entity.ksql_entity.ksql_Entity import ns as ksql_namespace

class flask_app(object):
    def __init__(self):
        self.app = Flask(__name__)

        logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
        logging.config.fileConfig(logging_conf_path)
        self.log = logging.getLogger(__name__)

    def configure_app(self):
        ## take values from settings.py
        # self.app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
        self.app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
        self.app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
        self.app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
        self.app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP

    def initialize_app(self):
        self.configure_app()
        blueprint = Blueprint('lin_api', __name__, url_prefix='/lin_api')
        api.init_app(blueprint)
        api.add_namespace(microservice_namespace)
        api.add_namespace(generic_process_namespace)
        api.add_namespace(connector_process_namespace)
        api.add_namespace(dashboard_entity_namespace)
        api.add_namespace(indexPattern_entity_namespace)
        api.add_namespace(visualization_entity_namespace)
        api.add_namespace(kafkaTopic_entity_namespace)
        api.add_namespace(elasticIndex_entity_namespace)
        api.add_namespace(confluentEnvironment_entity_namespace)
        api.add_namespace(kafkaCluster_entity_namespace)
        api.add_namespace(elasticCluster_entity_namespace)
        api.add_namespace(kibanaSpace_entity_namespace)
        api.add_namespace(kubernetes_environment_namespace)
        api.add_namespace(kubernetes_cluster_namespace)
        api.add_namespace(kubernetes_namespace_namespace)
        api.add_namespace(kubernetes_deployment_namespace)
        api.add_namespace(kubernetes_cronjob_namespace)
        api.add_namespace(kubernetes_pod_namespace)
        api.add_namespace(api_operation_process_namespace)
        api.add_namespace(ingress_controller_process_namespace)
        api.add_namespace(ingress_object_process_namespace)
        api.add_namespace(kubernetes_service_process_namespace)
        api.add_namespace(confluent_cloud_namespace)
        api.add_namespace(ksql_namespace)
        self.app.register_blueprint(blueprint)

    def run_app(self):
        self.log.info(
            '>>>>> Starting development server at http://{}/lin_api/ <<<<<'.format(self.app.config['SERVER_NAME']))
        self.app.run()


def init_config():
    store = ConfigStore.get_instance()

    store.load({
        **config,
        **credentials
    })
    register_atlas_entity_types(data_dictionary_entity_types)
    # register_atlas_entity_types(kubernetes_entity_types)
    # register_atlas_entity_types(connectors_entity_types)
    return store


# END init_config


def main():
    store = init_config()
    app_flask = flask_app()
    app_flask.initialize_app()
    app_flask.run_app()

def register_get_app():
    app_flask = flask_app()
    app_flask.initialize_app()
    register_shared(app_flask.app)
    return app_flask.app


if __name__ == "__main__":
    main()

""" TO RUN IN TERMINAL type: python -m .app

Make sure the localhost is available else it DOES NOT WORK!!!
"Not Found
The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."

Based Code from:
https://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/

PostMan - https://flask-restplus.readthedocs.io/en/stable/postman.html
"""
