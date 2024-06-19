import logging
from functools import partial
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


def handle_derived_entities_delete(  # noqa: PLR0913
    entity_guid: str,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
    relationship_attribute_guid: str,
    relationship_attribute_name: str,
) -> Dict[str, AppSearchDocument]:
    """
    Find related entities in Elasticsearch and update their references to the given entity.

    Parameters
    ----------
    entity_guid : str
        The GUID of the entity whose relationships are to be updated.
    entity_name : str
        The new name of the entity.
    elastic : Elasticsearch
        The Elasticsearch client instance.
    index_name : str
        The name of the Elasticsearch index.
    relationship_attribute_guid : str
        The field in the document representing the GUID of the relationship.
    relationship_attribute_name : str
        The field in the document representing the name of the relationship.
    relationship_attribute_type : str
        The field in the document representing the type of the relationship.

    Yields
    ------
    Generator[AppSearchDocument, None, None]
        Yields updated AppSearchDocument instances.
    """
    # Get the Elasticsearch documents for all related entities
    query = {
        "query": {
            "match": {
                relationship_attribute_guid: {
                    "query": entity_guid,
                    "operator": "and",
                },
            },
        },
    }

    logging.debug(
        "Searching for documents with relationship %s containing entity %s",
        relationship_attribute_guid,
        entity_guid,
    )

    for document in get_documents(query, elastic, index_name):
        if document.guid in updated_documents:
            document = updated_documents[document.guid]  # noqa: PLW2901

        # The query guarantees that the relationship attributes are present in the document.
        # No need for try/except block to handle a potential KeyError.
        guids: list[str] = getattr(document, relationship_attribute_guid)
        names: list[str] = getattr(document, relationship_attribute_name)

        try:
            index = guids.index(entity_guid)
        except ValueError:
            # Skip this document if the entity GUID is not found
            logging.exception(
                "Entity %s not found in relationship %s for document %s. Skipping document update.",
                entity_guid,
                relationship_attribute_guid,
                document.guid,
            )
            continue

        del guids[index]
        del names[index]

        logging.info("Deleted relationship %s for document %s", relationship_attribute_name, document.guid)
        logging.debug("Updated GUIDs: %s", guids)
        logging.debug("Updated names: %s", names)

        updated_documents[document.guid] = document

    return updated_documents


"""
Define a mapping of entity types to their relationships as represented in Elasticsearch.

This map is used to determine which relationships need to be updated when a particular entity
type is modified.
"""
RELATIONSHIP_MAP = {
    "m4i_data_domain": ["deriveddatadomain"],
    "m4i_data_entity": ["deriveddataentity"],
    "m4i_data_attribute": ["deriveddataattribute"],
    "m4i_field": ["derivedfield"],
    "m4i_dataset": ["deriveddataset"],
    "m4i_collection": ["derivedcollection"],
    "m4i_system": ["derivedsystem"],
    "m4i_person": ["derivedperson"],
    "m4i_generic_process": ["derivedprocess"],
}


"""
Create handlers for updating derived entities for each entity type.

Each handler is a partially applied function of `handle_derived_entities_update` customized for the
specific relationship of an entity type.

The `partial` function sets the `relationship_attribute_guid` and `relationship_attribute_name`
parameters for each handler based on the entity relationships defined in `RELATIONSHIP_MAP`.
"""
DERIVED_ENTITY_UPDATE_HANDLERS = {
    entity_type: [
        partial(
            handle_derived_entities_delete,
            relationship_attribute_guid=f"{relationship}guid",
            relationship_attribute_name=f"{relationship}",
        )
        for relationship in relationships
    ]
    for entity_type, relationships in RELATIONSHIP_MAP.items()
}


def handle_delete_derived_entities(
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Update derived entities in Elasticsearch based on the given EntityMessage.

    Parameters
    ----------
    message : EntityMessage
        The message containing details of the entity update.
    elastic : Elasticsearch
        The Elasticsearch client instance.
    index_name : str
        The name of the Elasticsearch index.

    Returns
    -------
    List[AppSearchDocument]
        A list of updated AppSearchDocument instances.

    Raises
    ------
    EntityDataNotProvidedError
        If the new_value attribute of the message is not provided.
    """
    entity_details = message.old_value

    if entity_details is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    entity_type = entity_details.type_name

    handlers = DERIVED_ENTITY_UPDATE_HANDLERS.get(entity_type, [])

    for handler in handlers:
        handler(entity_details.guid, elastic, index_name, updated_documents)

    return updated_documents
