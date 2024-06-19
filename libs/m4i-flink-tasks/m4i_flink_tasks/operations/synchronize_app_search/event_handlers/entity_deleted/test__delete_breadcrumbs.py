from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import Attributes, Entity, EntityAuditAction

from m4i_flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

from .delete_breadcrumbs import (
    EntityDataNotProvidedError,
    handle_delete_breadcrumbs,
)


def test__handle_update_breadcrumb_on_entity_delete() -> None:
    """
    Test the update of a document's breadcrumb information when an entity is deleted.

    Mocks
    -----
    - Mocks `get_documents` function to return a document that needs its breadcrumb updated.

    Asserts
    -------
    - The number of updated documents returned is 1.
    - The breadcrumb of the updated document does not include the deleted entity.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"name": "Data Domain Name"}),
        ),
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234", "3456"],
        breadcrumbname=["Data Domain Name", "Parent Entity Name"],
        breadcrumbtype=["m4i_data_domain", "m4i_data_entity"],
    )

    with patch(
        __package__ + ".delete_breadcrumbs.get_documents",
        return_value=[document_to_update],
    ):
        updated_documents = handle_delete_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 1

        updated_document = updated_documents["2345"]
        assert updated_document.guid == "2345"
        assert updated_document.breadcrumbguid == ["3456"]
        assert updated_document.breadcrumbname == ["Parent Entity Name"]
        assert updated_document.breadcrumbtype == ["m4i_data_entity"]


def test__handle_update_breadcrumb_removes_parents() -> None:
    """
    Test that the parents of the deleted entity are also removed from the breadcrumb.

    Mocks
    -----
    - Mocks `get_documents` function to return a document that needs its breadcrumb updated.

    Asserts
    -------
    - The number of updated documents returned is 1.
    - The breadcrumb of the updated document does not include the deleted entity or its parents.
    """
    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="3456",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="3456",
            type_name="m4i_data_entity",
            attributes=Attributes.from_dict({"name": "Parent Entity Name"}),
        ),
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234", "3456"],
        breadcrumbname=["Data Domain Name", "Parent Entity Name"],
        breadcrumbtype=["m4i_data_domain", "m4i_data_entity"],
    )

    with patch(
        __package__ + ".delete_breadcrumbs.get_documents",
        return_value=[document_to_update],
    ):
        updated_documents = handle_delete_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 1

        updated_document = updated_documents["2345"]
        assert updated_document.guid == "2345"
        assert updated_document.typename == "m4i_data_entity"
        assert updated_document.name == "Entity Name"
        assert updated_document.referenceablequalifiedname == "entity_name"
        assert updated_document.breadcrumbguid == []
        assert updated_document.breadcrumbname == []
        assert updated_document.breadcrumbtype == []


def test__handle_update_derived_entities_no_old_value() -> None:
    """
    Test handling of breadcrumb updates when the old_value attribute is missing.

    This test checks if the function raises an EntityDataNotProvidedError when the
    entity message lacks the 'old_value' attribute, which is essential for the breadcrumb update.

    Asserts
    -------
    - EntityDataNotProvidedError is raised.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
    )

    with pytest.raises(EntityDataNotProvidedError):
        handle_delete_breadcrumbs(message, Mock(), "test_index", {})


def test__handle_update_breadcrumbs_malformed_breadcrumb() -> None:
    """
    Test handling of breadcrumb updates when a document has a malformed breadcrumb.

    This test checks if the function correctly logs an error and skips the update when a document's
    breadcrumb is malformed (e.g., mismatched lengths of breadcrumb_guid and breadcrumb_name).

    Mocks
    -----
    - Mocks `get_documents` function to return a document with a malformed breadcrumb.

    Asserts
    -------
    - The function logs an error and does not update the malformed document.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"name": "Data Domain Name"}),
        ),
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234"],
        breadcrumbname=["Old Data Domain Name", "Old Data Domain Name"],
    )

    with patch(
        __package__ + ".delete_breadcrumbs.get_documents",
        return_value=[document_to_update],
    ), patch(
        __package__ + ".delete_breadcrumbs.logging.error",
    ) as mock_logger:
        updated_documents = handle_delete_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0

        mock_logger.assert_called_once_with(
            "Breadcrumb for document %s is malformed. Skipping document update.",
            document_to_update.guid,
        )


def test__handle_update_breadcrumbs_guid_not_present() -> None:
    """
    Test handling of breadcrumb updates when the entity's GUID is not present in the breadcrumb.

    This test checks if the function correctly skips the update when the entity's GUID is not found
    in the document's breadcrumb, despite the query indicating its presence.

    Mocks
    -----
    - Mocks `get_documents` to return a document without the entity's GUID in its breadcrumb.

    Asserts
    -------
    - The function skips updating the document where the entity's GUID is not found.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"name": "Data Domain Name"}),
        ),
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["5678"],
        breadcrumbname=["Old Data Domain Name"],
    )

    with patch(
        __package__ + ".delete_breadcrumbs.get_documents",
        return_value=[document_to_update],
    ):
        updated_documents = handle_delete_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0
