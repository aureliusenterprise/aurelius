import logging
from typing import Dict, Generator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from m4i_flink_tasks import AppSearchDocument, EntityMessage, SynchronizeAppSearchError
from m4i_flink_tasks.utils import ExponentialBackoff, retry


class EntityDataNotProvidedError(SynchronizeAppSearchError):
    """Exception raised when the entity details are not provided in the message."""

    def __init__(self, guid: str) -> None:
        """
        Initialize the exception.

        Parameters
        ----------
        guid : str
            The GUID of the entity for which the data was not provided.
        """
        super().__init__(f"Entity data not provided for entity {guid}")


class EntityNameNotFoundError(SynchronizeAppSearchError):
    """Exception raised when the entity name is not found in the entity details."""

    def __init__(self, guid: str) -> None:
        """
        Initialize the exception.

        Parameters
        ----------
        guid : str
            The GUID of the entity for which the name was not found.
        """
        super().__init__(f"Entity name not found for entity {guid}")


@retry(retry_strategy=ExponentialBackoff())
def get_documents(
    query: dict,
    elastic: Elasticsearch,
    index_name: str,
) -> Generator[AppSearchDocument, None, None]:
    """
    Yield AppSearchDocument objects from Elasticsearch based on the given query.

    Parameters
    ----------
    query : dict
        The Elasticsearch query used to fetch documents.
    elastic : Elasticsearch
        The Elasticsearch client instance.
    index_name : str
        The name of the index in Elasticsearch to query.

    Yields
    ------
    Generator[AppSearchDocument, None, None]
        Yields AppSearchDocument instances as they are retrieved from Elasticsearch.
    """
    for result in scan(elastic, index=index_name, query=query):
        yield AppSearchDocument.from_dict(result["_source"])


def update_document_breadcrumb(
    guid: str,
    name: str,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Update the breadcrumb information in documents related to a specified entity.

    This function searches for documents that reference the given entity in their breadcrumb and
    updates the entity's name in those breadcrumbs.

    Parameters
    ----------
    guid : str
        The GUID of the entity whose name in breadcrumbs needs to be updated.
    name : str
        The new name of the entity to update in breadcrumbs.
    elastic : Elasticsearch
        The Elasticsearch client instance for executing queries.
    index_name : str
        The name of the index in Elasticsearch.

    Yields
    ------
    Generator[AppSearchDocument, None, None]
        A generator of AppSearchDocument instances with modified breadcrumbs.
    """
    # Find all documents that reference the entity in their breadcrumb
    query = {"query": {"match": {"breadcrumbguid": {"query": guid, "operator": "and"}}}}

    logging.debug("Searching for documents with breadcrumb containing entity %s", guid)

    for document in get_documents(query, elastic, index_name):
        if document.guid in updated_documents:
            document = updated_documents[document.guid]  # noqa: PLW2901

        breadcrumb_guid = document.breadcrumbguid
        breadcrumb_name = document.breadcrumbname

        if len(breadcrumb_guid) != len(breadcrumb_name):
            logging.error(
                "Breadcrumb for document %s is malformed. Skipping document update.",
                document.guid,
            )
            continue

        try:
            index = breadcrumb_guid.index(guid)
        except ValueError:
            # The guid is not in the breadcrumb. Should not be possible given the query.
            logging.exception(
                "Entity %s not found in breadcrumb for document %s. Skipping document update.",
                guid,
                document.guid,
            )
            continue

        if breadcrumb_name[index] == name:
            # The name is already correct
            logging.debug(
                "Breadcrumb for document %s already has the correct name. Skipping document update.",
                document.guid,
            )
            continue

        breadcrumb_name[index] = name

        updated_documents[document.guid] = document

        logging.info("Updated breadcrumb for document %s: %s", document.guid, breadcrumb_name)

    return updated_documents


def handle_update_breadcrumbs(
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Handle the update of breadcrumb information in documents based on an entity update message.

    This function updates all breadcrumbs that include the name of the specified entity.

    Parameters
    ----------
    message : EntityMessage
        The message containing the update details of an entity.
    elastic : Elasticsearch
        The Elasticsearch client instance for document retrieval and update.
    index_name : str
        The name of the Elasticsearch index where documents are stored.

    Returns
    -------
    List[AppSearchDocument]
        A list of AppSearchDocument instances that have been updated.

    Raises
    ------
    EntityDataNotProvidedError
        If the entity's details are not provided in the message.
    EntityNameNotFoundError
        If the entity's name is not found in its details.
    """
    updated_attributes = set(message.inserted_attributes) | set(message.changed_attributes)

    if "name" not in updated_attributes:
        logging.debug("Name not updated. Skipping breadcrumb update.")
        return updated_documents

    entity_details = message.new_value

    if entity_details is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    entity_name = getattr(entity_details.attributes, "name", None)

    if entity_name is None:
        logging.error("Entity name not found for entity %s", entity_details.guid)
        raise EntityNameNotFoundError(entity_details.guid)

    return update_document_breadcrumb(entity_details.guid, entity_name, elastic, index_name, updated_documents)
