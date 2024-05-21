from pyflink.datastream import DataStream

from .operations import (
    ElasticsearchFactory,
    GetPreviousEntity,
)


class PublishState:
    """
    A class that orchestrates the entire process of handling Kafka notifications.

    This class initializes the various processing stages, including:

    - Retrieving previous entity versions from Elasticsearch
    - Preparing the validated notifications for indexing.

    Attributes
    ----------
    data_stream : DataStream
        The input Kafka notifications stream.
    previous_entity_retrieval : GetPreviousEntity
        Stage for retrieving the previous entity versions from Elasticsearch.
    index_preparation : PrepareNotificationToIndex
        Stage for preparing the validated notifications for indexing.
    errors : DataStream
        Aggregated stream of errors from the various processing stages.
    """

    def __init__(
        self,
        data_stream: DataStream,
        elastic_factory: ElasticsearchFactory,
        index_name: str,
    ) -> None:
        """
        Initialize the PublishState with an input Kafka notifications stream.

        Parameters
        ----------
        data_stream : DataStream
            The input stream of Kafka notifications.
        elastic_factory : ElasticsearchFactory
            A factory function for creating Elasticsearch clients.
        index_name : str
            The name of the Elasticsearch index to query.
        """
        self.data_stream = data_stream

        # Initialize the stage for retrieving the previous entity versions from a database.
        self.previous_entity_retrieval = GetPreviousEntity(
            self.data_stream,
            elastic_factory,
            index_name,
        )
