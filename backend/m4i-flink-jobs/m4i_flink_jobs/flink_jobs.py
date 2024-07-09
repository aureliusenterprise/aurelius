from typing import List, TypedDict, Union

from elastic_transport._models import DefaultType
from m4i_publish_state import main as publish_state
from m4i_synchronize_app_search import main as synchronize_app_search


class FlinkJobsConfig(TypedDict):
    """
    Configuration required to execute the SynchronizeAppSearch job.

    Attributes
    ----------
    elasticsearch_app_search_index_name: str
        The name of the index in Elasticsearch to which app search documents are synchronized.
    elasticsearch_publish_state_index_name: str
        The name of the index in Elasticsearch to which entity state is synchronized.
    elasticsearch_endpoint: str
        The endpoint URL for the Elasticsearch instance.
    elasticsearch_username: str
        The username for Elasticsearch authentication.
    elasticsearch_password: str
        The password for Elasticsearch authentication.
    kafka_app_search_topic_name: str
        The Kafka topic name to which updated App Search documents will be produced.
    kafka_bootstrap_server_hostname: str
        The hostname of the Kafka bootstrap server.
    kafka_bootstrap_server_port: str
        The port number of the Kafka bootstrap server.
    kafka_consumer_group_id: str
        The consumer group ID for Kafka.
    kafka_error_topic_name: str
        The Kafka topic name where errors will be published.
    kafka_producer_group_id: str
        The producer group ID for Kafka.
    kafka_source_topic_name: str
        The Kafka topic name from which data will be consumed.
    """

    atlas_server_url: str
    elasticsearch_app_search_index_name: str
    elasticsearch_publish_state_index_name: str
    elasticsearch_endpoint: str
    elasticsearch_username: str
    elasticsearch_password: str
    elasticsearch_certificate_path: Union[str, DefaultType]
    kafka_app_search_topic_name: str
    kafka_publish_state_topic_name: str
    kafka_bootstrap_server_hostname: str
    kafka_bootstrap_server_port: str
    kafka_consumer_group_id: str
    kafka_error_topic_name: str
    kafka_producer_group_id: str
    kafka_source_topic_name: str
    keycloak_client_id: str
    keycloak_client_secret_key: Union[str, None]
    keycloak_server_url: str
    keycloak_realm_name: str
    keycloak_username: str
    keycloak_password: str


def main(config: FlinkJobsConfig, jars_path: List[str]) -> None:
    synchronize_app_search(config, jars_path)
    publish_state(config, jars_path)
