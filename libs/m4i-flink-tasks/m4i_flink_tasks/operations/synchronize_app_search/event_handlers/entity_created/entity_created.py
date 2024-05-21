import logging
from typing import TYPE_CHECKING

from elasticsearch import Elasticsearch

from flink_tasks import AppSearchDocument, EntityMessage, SynchronizeAppSearchError
from flink_tasks.model.synchronize_app_search_error_with_payload import SynchronizeAppSearchWithPayloadError
from flink_tasks.operations.synchronize_app_search.event_handlers.relationship_audit.relationship_audit import (
    get_child_documents,
    get_related_documents,
)
from flink_tasks.utils import RetryError

if TYPE_CHECKING:
    from m4i_atlas_core import Entity

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

RELATIONSHIP_BLACKLIST = ["m4i_data_quality", "m4i_gov_data_quality", "m4i_source"]


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


def default_create_handler(  # noqa: C901, PLR0915, PLR0912
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: dict[str, AppSearchDocument],
) -> dict[str, AppSearchDocument]:
    """
    Create `AppSearchDocument` instance and update existing ones using the provided entity details.

    Parameters
    ----------
    message : EntityMessage
        The entity details to extract the necessary attributes from.
    elastic : Elasticsearch
        The Elasticsearch client for database interaction.
    index_name : str
        The name of the index in Elasticsearch to query.

    Returns
    -------
    AppSearchDocument
        List of AppSearchDocument instances representing the created entity and related entities.
    """
    if message.new_value is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    # Get attributes
    entity_details = message.new_value
    qualified_name = getattr(entity_details.attributes, "qualified_name", entity_details.guid)
    name = getattr(entity_details.attributes, "name", qualified_name)

    document = AppSearchDocument(
        id=message.new_value.guid,
        guid=message.new_value.guid,
        name=name,
        referenceablequalifiedname=qualified_name,
        supertypenames=[entity_details.type_name],
        typename=entity_details.type_name,
    )
    # Add document to created documents
    updated_documents[document.guid] = document

    parents = [parent.guid for parent in message.new_value.get_parents()]

    logging.info("Parents: %s", parents)

    inserted = [
        value for value in message.inserted_relationships.values() if value is not None
    ] if message.inserted_relationships else []

    logging.info("Relationships before filter (values): %s", inserted)

    inserted_relationships = [
        rel.guid
        for rels in inserted
        for rel in rels
        if (
            rel.guid is not None
            and getattr(rel, "type_name", None) not in RELATIONSHIP_BLACKLIST
        )
    ]

    logging.info("Relationships to insert: %s", inserted_relationships)

    related_documents = []

    try:
        related_documents = get_related_documents(inserted_relationships, elastic, index_name)
    except RetryError:
        logging.warning("Error retrieving related documents for entity %s.", message.guid)
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

    logging.info("Breadcrumb references %s. (%s)", breadcrumb_refs, inserted_relationships)

    # Add self to the breadcrumb refs in case of child -> parent relationship
    parents = {ref.guid for ref in message.new_value.get_parents() if ref.guid is not None}

    # Inserted relationship was a parent relation
    first_parent = next(iter(parents)) if parents else None

    if first_parent in inserted_relationships and first_parent in updated_documents:
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
            logging.warning("Child is not in updated_documents. GUID = %s", guid)
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


def create_person_handler(
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: dict[str, AppSearchDocument],
) -> dict[str, AppSearchDocument]:
    """
    Create an `AppSearchDocument` instance for a person entity using the provided entity details.

    Parameters
    ----------
    message : EntityMessage
        Message containing the person entity details to extract the necessary attributes from.
    elastic : Elasticsearch
        The Elasticsearch client for database interaction.
    index_name : str
        The name of the index in Elasticsearch to query.
    updated_documents : dict[str, AppSearchDocument]
        A dictionary containing the updated documents

    Returns
    -------
    AppSearchDocument
        The created AppSearchDocument instance.
    """
    if message.new_value is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    entity_details: Entity = message.new_value
    result = default_create_handler(message, elastic, index_name, updated_documents)

    attributes = entity_details.attributes

    if hasattr(attributes, "email"):
        logging.debug("Adding email to person entity: %s", entity_details.guid)
        result[entity_details.guid].email = attributes.email # type: ignore

    return result


ENTITY_CREATED_HANDLERS = {"m4i_person": create_person_handler}


def handle_entity_created(
    message: EntityMessage,
    elastic: Elasticsearch,
    index_name: str,
    updated_documents: dict[str, AppSearchDocument],
) -> dict[str, AppSearchDocument]:
    """
    Process the entity creation message and create `AppSearchDocument`s accordingly.

    EntityMessage should contain an entity from data_dictionary, so that
    the referred entities will not be an empty list.

    Parameters
    ----------
    message : EntityMessage
        The EntityMessage instance containing the entity creation details.
    elastic : Elasticsearch
        The Elasticsearch client for database interaction.
    index_name : str
        The name of the index in Elasticsearch to query.
    updated_documents : dict[str, AppSearchDocument]
        A dictionary containing the updated documents.

    Returns
    -------
    list[AppSearchDocument]
        A list containing the created and updated `AppSearchDocument`s.
        The first element is for the created entity.
        The rest is for its references.

    Raises
    ------
    EntityDataNotProvidedError
        If the entity details are not provided in the message.
    """
    entity_details = message.new_value

    logging.info("Creating entity from: %s", message)

    if entity_details is None:
        logging.error("Entity data not provided for entity %s", message.guid)
        raise EntityDataNotProvidedError(message.guid)

    create_handler = ENTITY_CREATED_HANDLERS.get(entity_details.type_name, default_create_handler)

    return create_handler(message, elastic, index_name, updated_documents)
