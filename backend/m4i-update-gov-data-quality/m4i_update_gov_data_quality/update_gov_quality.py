import json
from typing import List, TypedDict, Union

from elastic_transport._models import DefaultType
from keycloak import KeycloakOpenID
from m4i_flink_tasks.operations.get_rules.get_rules import GetRules
from pyflink.common import Configuration, Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    DeliveryGuarantee,
    FlinkKafkaConsumer,
    KafkaRecordSerializationSchema,
    KafkaSink,
)
import logging

class UpdateGovDataQualityConfig(TypedDict):
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
    kafka_gov_data_quality_topic_name
        The Kafka topic name to which governance data quality documents will be produced.
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
    kafka_gov_data_quality_topic_name: str
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

def log_and_transform(document):
    try:
        logging.info("Processing document: %s", document)
        transformed_document = json.dumps(
            {
                "id": document.guid,
                "value": json.loads(document.to_json()),
            }
        )
        logging.info("Successfully transformed document: %s", transformed_document)
        return transformed_document
    except Exception as e:
        logging.info("Error processing document with id: %s, error: %s", document.doc_id, str(e))
        raise

def main(config: UpdateGovDataQualityConfig, jars_path: List[str]) -> None:
    """Sink an example message into a Kafka topic."""

    env_config = Configuration()  # type: ignore
    env_config.set_string("restart-strategy.type", "fixed-delay")
    env_config.set_integer("restart-strategy.attempts", 999)

    env = StreamExecutionEnvironment.get_execution_environment(env_config)

    env.set_parallelism(1)
    env.add_jars(*jars_path)

    kafka_bootstrap_server = f"{config['kafka_bootstrap_server_hostname']}:{config['kafka_bootstrap_server_port']}"

    kafka_consumer = (
        FlinkKafkaConsumer(
            topics=config["kafka_publish_state_topic_name"], # Subscribe to publish state
            properties={
                "bootstrap.servers": kafka_bootstrap_server,
                "group.id": config["kafka_consumer_group_id"],
            },
            deserialization_schema=SimpleStringSchema(),
        )
        .set_commit_offsets_on_checkpoints(commit_on_checkpoints=True)
        .set_start_from_latest()
    )

    gov_data_quality_sink = (
        KafkaSink.builder()
        .set_bootstrap_servers(kafka_bootstrap_server)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(config["kafka_gov_data_quality_topic_name"])
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

    get_rules = GetRules(
        input_stream,
    )

    get_rules.main.map(
        lambda document: json.dumps(
            {
                "id": document[0],
                "value": document[1] if document[1] is None else document[1].to_dict()
            }
        ),
        Types.STRING(),
    ).sink_to(gov_data_quality_sink).name("Gov Data Quality Sink")


    env.execute("Gov Data Quality")
