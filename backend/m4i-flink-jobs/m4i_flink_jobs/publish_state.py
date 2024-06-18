import json
import os
from pathlib import Path
from typing import TypedDict, Union

from pyflink.common import Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    DeliveryGuarantee,
    FlinkKafkaConsumer,
    KafkaRecordSerializationSchema,
    KafkaSink,
)

from m4i_flink_tasks import GetEntity
from m4i_flink_tasks.operations.publish_state.operations import PrepareNotificationToIndex
from keycloak import KeycloakOpenID


class PublishStateConfig(TypedDict):
    """
    Configuration required to execute the PublishState job.

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


def main(config: PublishStateConfig) -> None:
    """Sink an example message into a Kafka topic."""
    env = StreamExecutionEnvironment.get_execution_environment()

    env.set_parallelism(1)

    # Add JARs to the classpath
    jars = [path.absolute().as_uri() for path in Path("./jars").glob("*.jar")]
    env.add_jars(*jars)

    kafka_bootstrap_server = f"{config['kafka_bootstrap_server_hostname']}:{config['kafka_bootstrap_server_port']}"

    kafka_consumer = (
        FlinkKafkaConsumer(
            topics=config["kafka_source_topic_name"],
            properties={
                "bootstrap.servers": kafka_bootstrap_server,
                "group.id": config["kafka_consumer_group_id"],
            },
            deserialization_schema=SimpleStringSchema(),
        )
        .set_commit_offsets_on_checkpoints(commit_on_checkpoints=True)
        .set_start_from_latest()
    )

    publish_state_sink = (
        KafkaSink.builder()
        .set_bootstrap_servers(kafka_bootstrap_server)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(config["kafka_publish_state_topic_name"])
            .set_key_serialization_schema(
                SimpleStringSchema(),
            )
            .set_value_serialization_schema(
                SimpleStringSchema(),
            )
            .build(),
        )
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE)
        .build()
    )

    (
        KafkaSink.builder()
        .set_bootstrap_servers(kafka_bootstrap_server)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(config["kafka_error_topic_name"])
            .set_value_serialization_schema(SimpleStringSchema())
            .build(),
        )
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE)
        .build()
    )

    def create_keycloak_client() -> KeycloakOpenID:
        """Create a Keycloak client instance."""
        return KeycloakOpenID(
            server_url=config["keycloak_server_url"],
            client_id=config["keycloak_client_id"],
            realm_name=config["keycloak_realm_name"],
            client_secret_key=config.get("keycloak_client_secret_key"),
        )

    input_stream = env.add_source(kafka_consumer).name("Kafka Source")

    get_entity = GetEntity(
        input_stream,
        config["atlas_server_url"],
        create_keycloak_client,
        (config["keycloak_username"], config["keycloak_password"]),
    )

    # Initialize the stage for preparing the validated notifications for indexing.
    publish_state_notification = PrepareNotificationToIndex(
        get_entity.main,
    )

    publish_state_notification.main.map(
        lambda document: json.dumps(
            {
                "id": document.doc_id,
                "value": json.loads(document.body.to_json()),
            },
        ),
        Types.STRING(),
    ).sink_to(publish_state_sink).name("Publish State Sink")

    #publish_state_notification.errors.map(
    #).sink_to(
    #    error_sink,
    #).name("Error Sink")

    env.execute("Publish state")


if __name__ == "__main__":
    """
    Entry point of the script. Load configuration from environment variables and start the job.
    """
    config: PublishStateConfig = {
        "atlas_server_url": os.environ["ATLAS_SERVER_URL"],
        "elasticsearch_app_search_index_name": os.environ["ELASTICSEARCH_APP_SEARCH_INDEX_NAME"],
        "elasticsearch_publish_state_index_name": os.environ["ELASTICSEARCH_STATE_INDEX_NAME"],
        "elasticsearch_endpoint": os.environ["ELASTICSEARCH_ENDPOINT"],
        "elasticsearch_username": os.environ["ELASTICSEARCH_USERNAME"],
        "elasticsearch_password": os.environ["ELASTICSEARCH_PASSWORD"],
        "kafka_app_search_topic_name": os.environ["KAFKA_APP_SEARCH_TOPIC_NAME"],
        "kafka_publish_state_topic_name": os.environ["KAFKA_PUBLISH_STATE_TOPIC_NAME"],
        "kafka_bootstrap_server_hostname": os.environ["KAFKA_BOOTSTRAP_SERVER_HOSTNAME"],
        "kafka_bootstrap_server_port": os.environ["KAFKA_BOOTSTRAP_SERVER_PORT"],
        "kafka_consumer_group_id": os.environ.get("CONSUMER_PUBLISH_STATE", "publish_state_group"),
        "kafka_error_topic_name": os.environ["KAFKA_ERROR_TOPIC_NAME"],
        "kafka_producer_group_id": os.environ["KAFKA_PRODUCER_GROUP_ID"],
        "kafka_source_topic_name": os.environ["KAFKA_SOURCE_TOPIC_NAME"],
        "keycloak_client_id": os.environ["KEYCLOAK_CLIENT_ID"],
        "keycloak_client_secret_key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
        "keycloak_password": os.environ["KEYCLOAK_PASSWORD"],
        "keycloak_realm_name": os.environ["KEYCLOAK_REALM_NAME"],
        "keycloak_server_url": os.environ["KEYCLOAK_SERVER_URL"],
        "keycloak_username": os.environ["KEYCLOAK_USERNAME"],
    }

    main(config)
