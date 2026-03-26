import logging

from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import KafkaException, NewTopic

LOGGER = logging.getLogger("KafkaAdminClient")

TOPIC_ALREADY_EXISTS = 36  # error code for topic already exists


class KafkaAdminClient:
    """A wrapper around the `AdminClient` from `confluent_kafka` that handles common workflows."""

    def __init__(self, admin_client: AdminClient) -> None:
        """
        Initialize the KafkaAdminClient with an AdminClient instance.

        Args:
            admin_client (AdminClient): The AdminClient instance to use internally.
        """
        self.admin_client = admin_client

    def create_topics(self, *topics: NewTopic) -> None:
        """
        Create the given Kafka topics.

        Args:
            topics (NewTopic): The topics to create.
        """
        operation = self.admin_client.create_topics(list(topics))

        for topic_name, future in operation.items():
            try:
                future.result()
                LOGGER.info("Topic %s created successfully", topic_name)
            except KafkaException as e:
                if e.args[0].code() == TOPIC_ALREADY_EXISTS:
                    LOGGER.warning("Topic %s already exists", topic_name)
                else:
                    LOGGER.exception("Topic %s could not be created", topic_name)
                    raise
