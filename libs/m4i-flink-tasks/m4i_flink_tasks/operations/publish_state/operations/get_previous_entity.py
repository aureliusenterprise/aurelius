import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from elasticsearch import ApiError, Elasticsearch
from m4i_atlas_core import AtlasChangeMessage, Entity, EntityAuditAction, get_entity_type_by_type_name
from pyflink.datastream import DataStream, MapFunction, RuntimeContext

from flink_tasks import AtlasChangeMessageWithPreviousVersion
from flink_tasks.operations.publish_state.operations.delayed_map import DelayedMap
from flink_tasks.utils import ExponentialBackoff, retry

ElasticsearchFactory = Callable[[], Elasticsearch]


@dataclass
class ElasticPreviousStateRetrieveError(Exception):
    """Exception raised for errors in the retrieval of previous state from ElasticSearch."""

    guid: str
    timestamp: int


class NoPreviousVersionError(ElasticPreviousStateRetrieveError):
    """Exception raised for errors in the retrieval of previous state from ElasticSearch."""

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return f"No previous version found for entity {self.guid} at {self.timestamp}."


class GetPreviousEntityFunction(MapFunction):
    """
    A custom `MapFunction` to retrieve the previous version of an entity from Elasticsearch.

    This function communicates with an Elasticsearch instance to obtain the previous version
    of an entity based on its GUID and creation time.

    Attributes
    ----------
    elastic_factory : ElasticClient
        Custom client for querying the desired Elasticsearch index.
    index_name : str
        The name of the index in Elasticsearch to which data is synchronized.
    """

    def __init__(self, elastic_factory: ElasticsearchFactory, index_name: str) -> None:
        """
        Initialize the `GetPreviousEntityFunction` instance.

        Parameters
        ----------
        elastic_factory : ElasticsearchFactory
            A factory function for creating Elasticsearch clients.
        """
        super().__init__()
        self.elastic_factory = elastic_factory
        self.index_name = index_name

    def open(self, context: RuntimeContext) -> None:  # noqa: ARG002
        """
        Initialize the Elasticsearch client.

        Parameters
        ----------
        context : RuntimeContext
            The context for this operator.
        """
        self.elasticsearch = self.elastic_factory()

    def map(
        self,
        value: AtlasChangeMessage | Exception,
    ) -> AtlasChangeMessageWithPreviousVersion | Exception:
        """
        Map function to retrieve the previous version of an entity.

        Parameters
        ----------
        value : ValidatedInput
            The input message containing the entity to lookup.

        Returns
        -------
        AtlasChangeMessageWithPreviousVersion or Exception
            The enriched message with the previous entity version or an error.
        """
        if isinstance(value, Exception):
            return value

        logging.debug("AtlasChangeMessage: %s", value)

        entity = value.message.entity

        if entity is None:
            logging.debug("Entity is required for lookup: %s", value)
            return ValueError("Entity is required for lookup")

        result = AtlasChangeMessageWithPreviousVersion(
            previous_version=None,
            version=value.version,
            message=value.message,
            msg_creation_time=value.msg_creation_time,
            msg_compression_kind=value.msg_compression_kind,
            msg_split_idx=value.msg_split_idx,
            msg_split_count=value.msg_split_count,
            msg_source_ip=value.msg_source_ip,
            msg_created_by=value.msg_created_by,
            spooled=value.spooled,
        )

        if value.message.operation_type == EntityAuditAction.ENTITY_CREATE:
            return result

        msg_creation_time = value.msg_creation_time

        try:
            result.previous_version = self.get_previous_entity(entity, msg_creation_time)
        except ApiError as e:
            return ValueError(str(e))
        except NoPreviousVersionError as e:
            return e
        return result

    def close(self) -> None:
        """Close the Elasticsearch client."""
        self.elasticsearch.close()

    @retry(retry_strategy=ExponentialBackoff(), catch=(ApiError, NoPreviousVersionError))
    def get_previous_entity(
        self,
        current_version: Entity,
        timestamp: int,
    ) -> Entity:
        """Retrieve the previous version of an entity from ElasticSearch."""
        query = {
            "bool": {
                "filter": [
                    {
                        "match": {
                            "guid.keyword": {
                                "query": current_version.guid,
                                "operator": "and",
                            },

                        },
                    },
                    {
                        "range": {
                            "updateTime": {
                                "lt": timestamp,
                            },
                        },
                    },
                ],
            },
        }

        sort = {
            "updateTime": {"numeric_type": "long", "order": "desc"},
        }

        search_result = self.elasticsearch.search(
            index=self.index_name,
            query=query,
            sort=sort,
            size=1,
        )

        if search_result["hits"]["total"]["value"] == 0:
            logging.error("No previous version found for entity %s at %s. (%s)",
                          current_version.guid, timestamp, int(1000*time.time()))
            raise NoPreviousVersionError(current_version.guid, timestamp)

        entity_type = get_entity_type_by_type_name(current_version.type_name)

        return entity_type.from_dict(search_result["hits"]["hits"][0]["_source"])


class GetPreviousEntity:
    """
    A class that sets up the Flink data stream for retrieving previous entity versions.

    This class initializes the data stream and applies the `GetPreviousEntityFunction`
    to fetch the previous entity versions. It organizes the output into `main`,
    `elastic_errors`, `no_previous_entity_errors`, and `errors` streams.

    Attributes
    ----------
    input_stream : DataStream
        The input stream of validated messages.
    main : DataStream
        The main output stream containing messages with previous entities.
    elastic_factory : ElasticsearchFactory
        Elasticsearch low-level client.
    """

    def __init__(
        self,
        input_stream: DataStream,
        elastic_factory: ElasticsearchFactory,
        index_name: str,
    ) -> None:
        """
        Initialize `GetPreviousEntity` with an input data stream.

        Parameters
        ----------
        input_stream : DataStream
            The input stream of validated notifications.
        elastic_factory : ElasticsearchFactory
            A factory function for creating Elasticsearch clients.
        index_name : str
            The name of the Elasticsearch index to query.
        """
        self.input_stream = input_stream
        self.elastic_factory = elastic_factory

        self.main = self.input_stream.map(DelayedMap()).map(
            GetPreviousEntityFunction(elastic_factory, index_name),
        ).name("previous_entity_lookup")
