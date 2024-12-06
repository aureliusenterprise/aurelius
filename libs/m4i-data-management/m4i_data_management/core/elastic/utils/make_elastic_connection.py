from elasticsearch import Elasticsearch
from m4i_atlas_core.config.config_store import ConfigStore

config = ConfigStore.get_instance()


def make_elastic_connection() -> Elasticsearch:
    """
    Returns a connection with the ElasticSearch database in the Data Management Platform
    """

    cloud_id, username, password, scheme, port = config.get_many(
        "elastic.cloud.id",
        "elastic.cloud.username",
        "elastic.cloud.password",
        "elastic.cloud.scheme",
        "elastic.cloud.port"
    )

    connection_config = {
        "cloud_id": cloud_id,
        "http_auth": (
            username,
            password
        ),
        "scheme": scheme,
        "port": port
    }

    connection = Elasticsearch(
        **connection_config
    )

    return connection
# END make_elastic_connection
