import os
from pathlib import Path

from elastic_transport._models import DefaultType
from m4i_flink_jobs import FlinkJobsConfig, main

if __name__ == "__main__":
    """
    Entry point of the script. Load configuration from environment variables and start the job.
    """
    config: FlinkJobsConfig = {
        "atlas_server_url": os.environ["ATLAS_SERVER_URL"],
        "elasticsearch_app_search_index_name": os.environ[
            "ELASTICSEARCH_APP_SEARCH_INDEX_NAME"
        ],
        "elasticsearch_publish_state_index_name": os.environ[
            "ELASTICSEARCH_STATE_INDEX_NAME"
        ],
        "elasticsearch_endpoint": os.environ["ELASTICSEARCH_ENDPOINT"],
        "elasticsearch_username": os.environ["ELASTICSEARCH_USERNAME"],
        "elasticsearch_password": os.environ["ELASTICSEARCH_PASSWORD"],
        "elasticsearch_certificate_path": os.environ.get(
            "ELASTICSEARCH_CERTIFICATE_PATH", DefaultType(0)
        ),
        "kafka_app_search_topic_name": os.environ["KAFKA_APP_SEARCH_TOPIC_NAME"],
        "kafka_publish_state_topic_name": os.environ["KAFKA_PUBLISH_STATE_TOPIC_NAME"],
        "kafka_bootstrap_server_hostname": os.environ[
            "KAFKA_BOOTSTRAP_SERVER_HOSTNAME"
        ],
        "kafka_bootstrap_server_port": os.environ["KAFKA_BOOTSTRAP_SERVER_PORT"],
        "kafka_consumer_group_id": os.environ["KAFKA_CONSUMER_GROUP_ID"],
        "kafka_error_topic_name": os.environ["KAFKA_ERROR_TOPIC_NAME"],
        "kafka_producer_group_id": os.environ["KAFKA_PRODUCER_GROUP_ID"],
        "kafka_source_topic_name": os.environ["KAFKA_SOURCE_TOPIC_NAME"],
        "kafka_gov_data_quality_topic_name": os.environ["KAFKA_GOV_DATA_QUALITY_TOPIC_NAME"],
        "keycloak_client_id": os.environ["KEYCLOAK_CLIENT_ID"],
        "keycloak_client_secret_key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
        "keycloak_password": os.environ["KEYCLOAK_PASSWORD"],
        "keycloak_realm_name": os.environ["KEYCLOAK_REALM_NAME"],
        "keycloak_server_url": os.environ["KEYCLOAK_SERVER_URL"],
        "keycloak_username": os.environ["KEYCLOAK_USERNAME"],
    }

    jars_root = Path(__file__).parent / "jars"
    jars_path = [path.absolute().as_uri() for path in jars_root.glob("*.jar")]

    main(config, jars_path)
