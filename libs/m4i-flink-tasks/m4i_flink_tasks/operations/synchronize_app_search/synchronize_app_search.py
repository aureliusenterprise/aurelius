import logging
from collections.abc import Callable
from functools import reduce

from elasticsearch import Elasticsearch
from pyflink.datastream import DataStream, MapFunction, OutputTag, RuntimeContext

from flink_tasks import (
    AppSearchDocument,
    EntityMessage,
    EntityMessageType,
    SynchronizeAppSearchError,
)

from .event_handlers import (
    handle_delete_breadcrumbs,
    handle_delete_derived_entities,
    handle_entity_created,
    handle_relationship_audit,
    handle_update_attributes,
    handle_update_breadcrumbs,
    handle_update_derived_entities,
)

ElasticsearchFactory = Callable[[], Elasticsearch]
EventHandler = Callable[[EntityMessage, Elasticsearch, str, dict[str, AppSearchDocument]], dict[str, AppSearchDocument]]

EVENT_HANDLERS: dict[EntityMessageType, list[EventHandler]] = {
    EntityMessageType.ENTITY_CREATED: [handle_entity_created],
    EntityMessageType.ENTITY_ATTRIBUTE_AUDIT: [
        handle_update_attributes,
        handle_update_breadcrumbs,
        handle_update_derived_entities,
    ],
    EntityMessageType.ENTITY_DELETED: [handle_delete_breadcrumbs, handle_delete_derived_entities],
    EntityMessageType.ENTITY_RELATIONSHIP_AUDIT: [handle_relationship_audit],
}

UNKNOWN_EVENT_TYPE_TAG = OutputTag("unknown_event_type")
SYNCHRONIZE_APP_SEARCH_ERROR_TAG = OutputTag("synchronize_app_search_error")


class SynchronizeAppSearchFunction(MapFunction):
    """
    Updates Elasticsearch with the changes in the incoming data stream.

    Attributes
    ----------
    elastic_factory : ElasticsearchFactory
        A factory function that returns an Elasticsearch client instance.
    index_name : str
        The name of the index in Elasticsearch to which data is synchronized.
    """

    def __init__(self, elastic_factory: ElasticsearchFactory, index_name: str) -> None:
        """
        Initialize the SynchronizeAppSearchFunction.

        Parameters
        ----------
        elastic_factory : ElasticsearchFactory
            A factory function that returns an Elasticsearch client instance.
        index_name : str
            The name of the index in Elasticsearch to which data is synchronized.
        """
        self.elastic_factory = elastic_factory
        self.index_name = index_name

    def open(self, runtime_context: RuntimeContext) -> None:  # noqa: ARG002
        """
        Initialize the Elasticsearch client. This method is called when the function is opened.

        Parameters
        ----------
        runtime_context : RuntimeContext
            The runtime context in which the function is executed.
        """
        self.elastic = self.elastic_factory()

    def map(
        self,
        value: EntityMessage | Exception,
    ) -> list[tuple[str, AppSearchDocument | None]] | list[Exception]:
        """
        Process an EntityMessage and perform actions based on the type of change event.

        Parameters
        ----------
        value : EntityMessage
            The message to be processed.

        Returns
        -------
        list[tuple[str, AppSearchDocument | None]] | list[Exception]
            A list of tuples containing document GUIDs and documents, or a list of Exceptions.
        """
        if isinstance(value, Exception):
            logging.debug("Passing down error: %s", value)
            return [value]

        logging.info("SynchronizeAppSearchFunction: %s", value)

        event_type = value.event_type

        if event_type not in EVENT_HANDLERS:
            message = f"Unknown event type: {event_type}"
            logging.error(message)
            return [NotImplementedError(message)]

        event_handlers = EVENT_HANDLERS[event_type]

        updated_documents: dict[str, AppSearchDocument] = {}

        try:
            updated_documents = reduce(
                lambda docs, handler: handler(value, self.elastic, self.index_name, docs),
                event_handlers,
                {},
            )

            if event_type == EntityMessageType.ENTITY_DELETED:
                updated_documents[value.guid] = None  # type: ignore
        except SynchronizeAppSearchError as e:
            return [e]

        result = list(updated_documents.items())

        logging.info("Updated documents: %s", result)

        return result  # type: ignore

    def close(self) -> None:
        """Close the Elasticsearch client. This method is called when the function is closed."""
        self.elastic.close()


class SynchronizeAppSearch:
    """
    Sets up a data stream for synchronizing App Search documents based on incoming change events.

    Attributes
    ----------
    data_stream : DataStream
        The data stream that contains change messages.
    app_search_documents : DataStream
        The processed stream of App Search documents as a batch per change.
    main : DataStream
        The stream of individual App Search documents.
    """

    def __init__(
            self,
            data_stream: DataStream,
            elastic_factory: ElasticsearchFactory,
            index_name: str,
    ) -> None:
        self.data_stream = data_stream

        self.app_search_documents = self.data_stream.map(
            SynchronizeAppSearchFunction(elastic_factory, index_name),
        ).name("synchronize_app_search")

        self.main = self.app_search_documents.flat_map(
            lambda documents: (
                document for document in documents if not isinstance(document, Exception)
            ),
        ).name("app_search_documents")
