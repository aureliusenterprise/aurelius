import logging
from typing import Dict, List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from m4i_flink_tasks import AppSearchDocument, EntityMessage, SynchronizeAppSearchError
from m4i_flink_tasks.model.synchronize_app_search_error_with_payload import SynchronizeAppSearchWithPayloadError
from m4i_flink_tasks.utils import ExponentialBackoff, RetryError, retry

RELATIONSHIP_MAP = {
    "m4i_data_domain": "deriveddatadomain",
    "m4i_data_entity": "deriveddataentity",
    "m4i_data_attribute": "deriveddataattribute",
    "m4i_field": "derivedfield",
    "m4i_dataset": "deriveddataset",
    "m4i_collection": "derivedcollection",
    "m4i_system": "derivedsystem",
    "m4i_person": "derivedperson",
    "m4i_generic_process": "derivedprocess",
}


class AppSearchDocumentNotFoundError(SynchronizeAppSearchError):
    """Exception raised when the AppSearchDocument is not found in the index."""

    def __init__(self, guid: str) -> None:
        """
        Initialize the exception.

        Parameters
        ----------
        guid : str
            The GUID of the entity for which the document was not found.
        """
        super().__init__(f"AppSearchDocument not found for entity {guid}")


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
def get_current_document(guid: str, elastic: Elasticsearch, index_name: str) -> AppSearchDocument:
    """
    Get the document representing the entity with the given id from the Elasticsearch index.

    Parameters
    ----------
    guid : str
        The unique id of the entity.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.

    Returns
    -------
    AppSearchDocument
        The AppSearchDocument instance.
    """
    logging.debug("Getting document with id %s", guid)

    result = elastic.get(index=index_name, id=guid)

    if not result.body["found"]:
        raise AppSearchDocumentNotFoundError(guid)

    return AppSearchDocument.from_dict(result.body["_source"])


@retry(retry_strategy=ExponentialBackoff(), max_retries=2)
def get_related_documents(
    ids: List[str],
    elastic: Elasticsearch,
    index_name: str,
) -> List[AppSearchDocument]:
    """
    Get the related documents from the Elasticsearch index.

    Parameters
    ----------
    ids : list[str]
        The list of GUIDs of the related documents.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.

    Returns
    -------
    List[AppSearchDocument]
        A list of the related AppSearchDocument instances as they are retrieved from Elasticsearch.
    """
    if not ids:
        return []

    # Make an exact match on several guid with or clause
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"guid": {"query": guid, "operator": "and"}}}
                    for guid in ids
                ],
            },
        },
    }

    logging.debug("Searching for related documents with %s", query)

    results = [
        AppSearchDocument.from_dict(search_result["_source"])
        for search_result in scan(elastic, index=index_name, query=query)
    ]

    if len(results) != len(ids):
        message = f"Some related documents were not found in the index. ({results}/{ids})"
        raise SynchronizeAppSearchWithPayloadError(message, results)

    return results


@retry(retry_strategy=ExponentialBackoff())
def get_child_documents(
    ids: List[str],
    elastic: Elasticsearch,
    index_name: str,
) -> List[AppSearchDocument]:
    """
    Get the related documents from the Elasticsearch index.

    Parameters
    ----------
    ids : list[str]
        The list of GUIDs of the direct child documents.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.

    Returns
    -------
    List[AppSearchDocument]
        Yields the related AppSearchDocument instances as they are retrieved from Elasticsearch.
    """
    if not ids:
        return []

    # Make an exact match on several breadcrumbguid with or clause
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"breadcrumbguid": {"query": guid, "operator": "and"}}}
                    for guid in ids
                ],
            },
        },
    }

    logging.debug("Searching for child documents with breadcrumb: query = %s", query)

    return [
        AppSearchDocument.from_dict(search_result["_source"])
        for search_result in scan(elastic, index=index_name, query=query)
    ]


def handle_deleted_relationships(  # noqa: C901, PLR0915, PLR0912
    message: EntityMessage,
    document: AppSearchDocument,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Handle the deleted relationships in the entity message.

    Parameters
    ----------
    message : EntityMessage
        The message containing the entity details and the relationships.
    document : AppSearchDocument
        The AppSearchDocument of the entity.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.
    updated_documents : Dict[str, AppSearchDocument]
        The dictionary of updated AppSearchDocuments.
    """
    if message.deleted_relationships is None:
        logging.warning("Deleted relationships not provided for entity %s", message.guid)
        return updated_documents

    if message.old_value is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    parents = [parent.guid for parent in message.old_value.get_parents()]

    deleted_relationships = [
        rel.guid
        for rels in message.deleted_relationships.values()
        for rel in rels
        if rel.guid is not None and rel.guid not in parents
    ]

    logging.info("Relationships to delete: %s", deleted_relationships)

    if not deleted_relationships:
        logging.info("No relationships to delete for entity %s", message.guid)
        return updated_documents

    related_documents = []

    try:
        related_documents = get_related_documents(deleted_relationships, elastic, index_name)
    except RetryError:
        logging.warning("Error retrieving related documents for entity %s", message.guid)
    except SynchronizeAppSearchWithPayloadError as e:
        related_documents = e.partial_result
        logging.warning("Gave up retrieving all documents")

    logging.info("Found related documents: %s", related_documents)

    for related_document in related_documents:
        if related_document.guid in updated_documents:
            related_document = updated_documents[related_document.guid]  # noqa: PLW2901

        if related_document.typename not in RELATIONSHIP_MAP or document.typename not in RELATIONSHIP_MAP:
            logging.warning("Entity is not mapped. (%s %s)", related_document.guid, related_document.typename)
            continue

        field = RELATIONSHIP_MAP[related_document.typename]
        related_field = RELATIONSHIP_MAP[document.typename]

        guids: list[str] = getattr(document, f"{field}guid")
        names: list[str] = getattr(document, field)

        if related_document.guid in guids:
            idx = guids.index(related_document.guid)

            guids.pop(idx)
            names.pop(idx)

        logging.info("Deleted relationship %s for entity %s", document.typename, document.guid)
        logging.debug("Updated ids: %s", guids)
        logging.debug("Updated names: %s", names)

        related_guids: list[str] = getattr(related_document, f"{related_field}guid")
        related_names: list[str] = getattr(related_document, related_field)

        if document.guid in related_guids:
            idx = related_guids.index(document.guid)

            related_guids.pop(idx)
            related_names.pop(idx)

        logging.info("Deleted relationship %s for entity %s", related_document.typename, related_document.guid)
        logging.debug("Updated ids: %s", related_guids)
        logging.debug("Updated names: %s", related_names)

        updated_documents[document.guid] = document
        updated_documents[related_document.guid] = related_document

    breadcrumb_refs = {
        child.guid
        for child in message.old_value.get_children()
        if child.guid is not None and child.guid in deleted_relationships
    }

    parents = {ref.guid for ref in message.old_value.get_parents() if ref.guid is not None}
    remaining_parent_relationships = list(parents.difference(deleted_relationships))

    if len(remaining_parent_relationships) < len(parents):
        parent_document = updated_documents[remaining_parent_relationships[0]]

        document.breadcrumbguid = [
            *parent_document.breadcrumbguid,
            parent_document.guid,
        ]

        document.breadcrumbname = [
            *parent_document.breadcrumbname,
            parent_document.name,
        ]

        document.breadcrumbtype = [
            *parent_document.breadcrumbtype,
            parent_document.typename,
        ]

        document.parentguid = parent_document.guid

        logging.info("Set parent of entity %s to %s", document.guid, parent_document.guid)
        logging.info("Breadcrumb GUID: %s", document.breadcrumbguid)
        logging.info("Breadcrumb Name: %s", document.breadcrumbname)
        logging.info("Breadcrumb Type: %s", document.breadcrumbtype)

        updated_documents[document.guid] = document

    elif len(remaining_parent_relationships) == 0:
        document.breadcrumbguid = []
        document.breadcrumbname = []
        document.breadcrumbtype = []

        document.parentguid = None

        logging.info("Removed parent of entity %s", document.guid)

        updated_documents[document.guid] = document

    immediate_children = {
        child.guid
        for child in message.old_value.get_children()
        if child.guid is not None and child.guid in deleted_relationships
    }

    logging.info("Immediate children: %s", immediate_children)

    # delete immediate children relation
    for child_guid in immediate_children:
        child_document = updated_documents[child_guid]

        logging.info("Set parent relationship of entity %s to %s", child_document.guid, child_document.parentguid)

        # Query guarantees that the breadcrumb includes the guid.
        idx = child_document.breadcrumbguid.index(document.guid)

        child_document.breadcrumbguid = child_document.breadcrumbguid[idx + 1 :]
        child_document.breadcrumbname = child_document.breadcrumbname[idx + 1 :]
        child_document.breadcrumbtype = child_document.breadcrumbtype[idx + 1 :]
        child_document.parentguid = child_document.breadcrumbguid[-1] if child_document.breadcrumbguid else None

        logging.info("Breadcrumb GUID: %s", child_document.breadcrumbguid)
        logging.info("Breadcrumb Name: %s", child_document.breadcrumbname)
        logging.info("Breadcrumb Type: %s", child_document.breadcrumbtype)

        updated_documents[child_document.guid] = child_document

    logging.info("Deletion operation - breadcrumb_refs %s", list(breadcrumb_refs))

    for child_document in get_child_documents(
        list(breadcrumb_refs),
        elastic,
        index_name,
    ):
        if child_document.guid in updated_documents:
            child_document = updated_documents[child_document.guid]  # noqa: PLW2901

        logging.info("Set parent relationship of entity %s to %s", child_document.guid, child_document.parentguid)

        try:
            # Query guarantees that the breadcrumb includes the guid.
            idx = child_document.breadcrumbguid.index(document.guid)
        except ValueError:
            logging.exception("Document is not in child document breadcrumb (%s)", child_document.guid)
            continue

        child_document.breadcrumbguid = child_document.breadcrumbguid[idx + 1 :]
        child_document.breadcrumbname = child_document.breadcrumbname[idx + 1 :]
        child_document.breadcrumbtype = child_document.breadcrumbtype[idx + 1 :]
        child_document.parentguid = child_document.breadcrumbguid[-1] if child_document.breadcrumbguid else None

        logging.info("Breadcrumb GUID: %s", child_document.breadcrumbguid)
        logging.info("Breadcrumb Name: %s", child_document.breadcrumbname)
        logging.info("Breadcrumb Type: %s", child_document.breadcrumbtype)

        updated_documents[child_document.guid] = child_document

    return updated_documents


def handle_inserted_relationships(  # noqa: C901, PLR0912, PLR0915
    message: EntityMessage,
    document: AppSearchDocument,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Handle the inserted relationships in the entity message.

    Parameters
    ----------
    message : EntityMessage
        The message containing the entity details and the relationships.
    document : AppSearchDocument
        The AppSearchDocument of the entity.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.
    updated_documents : Dict[str, AppSearchDocument]
        The dictionary of updated AppSearchDocuments.
    """
    if message.inserted_relationships is None:
        logging.warning("Inserted relationships not provided for entity %s", message.guid)
        return updated_documents

    if message.new_value is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    parents = [parent.guid for parent in message.new_value.get_parents()]

    logging.info("Relationships before filter: %s", message.inserted_relationships)

    inserted_relationships = [
        rel.guid
        for rels in message.inserted_relationships.values()
        for rel in rels
        if rel.guid is not None and rel.guid not in parents
    ]

    logging.info("Relationships to insert: %s", inserted_relationships)
    logging.info("Parents: %s", parents)

    if not inserted_relationships:
        logging.info("No relationships to insert for entity %s", message.guid)
        return updated_documents

    try:
        related_documents = get_related_documents(inserted_relationships, elastic, index_name)
    except RetryError as e:
        logging.exception("Error retrieving related documents for entity %s", message.guid)
        raise SynchronizeAppSearchError(message) from e

    for related_document in related_documents:
        if related_document.guid in updated_documents:
            related_document = updated_documents[related_document.guid]  # noqa: PLW2901

        if related_document.typename not in RELATIONSHIP_MAP or document.typename not in RELATIONSHIP_MAP:
            logging.warning("Entity is not mapped. (%s %s)", related_document.guid, related_document.typename)
            continue

        field = RELATIONSHIP_MAP[related_document.typename]
        related_field = RELATIONSHIP_MAP[document.typename]

        guids: list[str] = getattr(document, f"{field}guid")
        names: list[str] = getattr(document, field)

        if related_document.guid not in guids:
            guids.append(related_document.guid)
            names.append(related_document.name)

        logging.info("Inserted relationship %s for entity %s", document.typename, document.guid)
        logging.debug("Updated ids: %s", guids)
        logging.debug("Updated names: %s", names)

        related_guids: list[str] = getattr(related_document, f"{related_field}guid")
        related_names: list[str] = getattr(related_document, related_field)

        if document.guid not in related_guids:
            related_guids.append(document.guid)
            related_names.append(document.name)

        logging.info("Inserted relationship %s for entity %s", related_document.typename, related_document.guid)
        logging.debug("Updated ids: %s", related_guids)
        logging.debug("Updated names: %s", related_names)

        updated_documents[document.guid] = document
        updated_documents[related_document.guid] = related_document

    if message.new_value is None:
        return updated_documents

    breadcrumb_refs = {
        child.guid
        for child in message.new_value.get_children()
        if child.guid is not None and child.guid in inserted_relationships
    }

    logging.info("Breadcrumb references: %s. (%s)", breadcrumb_refs, inserted_relationships)

    # Add self to the breadcrumb refs in case of child -> parent relationship
    parents = {ref.guid for ref in message.new_value.get_parents() if ref.guid is not None}

    # Inserted relationship was a parent relation
    first_parent = next(iter(parents)) if parents else None

    if first_parent in inserted_relationships:
        parent_doc = updated_documents[first_parent]

        if parent_doc.guid not in document.breadcrumbguid:
            document.breadcrumbname = [
                *parent_doc.breadcrumbname,
                parent_doc.name,
            ]
            document.breadcrumbguid = [
                *parent_doc.breadcrumbguid,
                parent_doc.guid,
            ]
            document.breadcrumbtype = [
                *parent_doc.breadcrumbtype,
                parent_doc.typename,
            ]

            document.parentguid = parent_doc.guid

            logging.info("Set parent of entity %s to %s", document.guid, parent_doc.guid)
            logging.info("Breadcrumb GUID: %s", document.breadcrumbguid)
            logging.info("Breadcrumb Name: %s", document.breadcrumbname)
            logging.info("Breadcrumb Type: %s", document.breadcrumbtype)

            # update main entity
            updated_documents[document.guid] = document

    immediate_children = {
        child.guid
        for child in message.new_value.get_children()
        if child.guid is not None and child.guid in inserted_relationships
    }

    logging.info("Immediate children %s. (%s)", immediate_children, inserted_relationships)

    # update immediate children
    for guid in list(immediate_children):
        # update children breadcrumb

        if guid not in updated_documents:
            logging.error("Immediate children not found in updated_documents %s", guid)
            continue

        child_doc = updated_documents[guid]

        if document.guid in child_doc.breadcrumbguid:
            continue

        child_doc.breadcrumbname = [
            *document.breadcrumbname,
            document.name,
        ]

        child_doc.breadcrumbguid = [
            *document.breadcrumbguid,
            document.guid,
        ]

        child_doc.breadcrumbtype = [
            *document.breadcrumbtype,
            document.typename,
        ]

        child_doc.parentguid = document.guid

        logging.info("Set parent relationship of entity %s to %s", child_doc.guid, child_doc.parentguid)
        logging.debug("Breadcrumb GUID: %s", child_doc.breadcrumbguid)
        logging.debug("Breadcrumb Name: %s", child_doc.breadcrumbname)
        logging.debug("Breadcrumb Type: %s", child_doc.breadcrumbtype)

        updated_documents[guid] = child_doc

    for child_document in get_child_documents(
        list(breadcrumb_refs),
        elastic,
        index_name,
    ):
        if child_document.guid in immediate_children:
            continue

        if child_document.guid in updated_documents:
            child_document = updated_documents[child_document.guid]  # noqa: PLW2901

        # If breadcrumb already contains the id of the current element, skip to avoid cycles in the breadcrumb
        if document.guid in child_document.breadcrumbguid:
            continue

        child_document.breadcrumbguid = [
            *document.breadcrumbguid,
            document.guid,
            *child_document.breadcrumbguid,
        ]

        child_document.breadcrumbname = [
            *document.breadcrumbname,
            document.name,
            *child_document.breadcrumbname,
        ]

        child_document.breadcrumbtype = [
            *document.breadcrumbtype,
            document.typename,
            *child_document.breadcrumbtype,
        ]

        child_document.parentguid = child_document.breadcrumbguid[-1] if child_document.breadcrumbguid else None

        logging.info("Set parent relationship of entity %s to %s", child_document.guid, child_document.parentguid)
        logging.debug("Breadcrumb GUID: %s", child_document.breadcrumbguid)
        logging.debug("Breadcrumb Name: %s", child_document.breadcrumbname)
        logging.debug("Breadcrumb Type: %s", child_document.breadcrumbtype)

        updated_documents[child_document.guid] = child_document

    return updated_documents


def handle_relationship_audit(
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: Dict[str, AppSearchDocument],
) -> Dict[str, AppSearchDocument]:
    """
    Handle the relationship audit event.

    Parameters
    ----------
    message : EntityMessage
        The message containing the entity details and the relationships.
    elastic : Elasticsearch
        The Elasticsearch client.
    index_name : str
        The name of the index.

    Returns
    -------
    List[AppSearchDocument]
        The list of updated AppSearchDocuments.
    """
    if not (message.inserted_relationships or message.deleted_relationships):
        logging.info("No relationships to update for entity %s", message.guid)
        return updated_documents

    if message.guid in updated_documents:
        document = updated_documents[message.guid]
    else:
        document = get_current_document(message.guid, elastic, index_name)

    updated_documents = handle_deleted_relationships(
        message,
        document,
        elastic,
        index_name,
        updated_documents,
    )

    updated_documents = handle_inserted_relationships(
        message,
        document,
        elastic,
        index_name,
        updated_documents,
    )

    if document.guid in updated_documents:
        doc = updated_documents[document.guid]
        updated_documents[doc.guid].parentguid = doc.breadcrumbguid[-1] if doc.breadcrumbguid else None

    return updated_documents
