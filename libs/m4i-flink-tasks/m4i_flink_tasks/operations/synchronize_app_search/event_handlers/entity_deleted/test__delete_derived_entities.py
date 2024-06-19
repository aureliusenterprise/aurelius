from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import Attributes, Entity, EntityAuditAction

from m4i_flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

from .delete_derived_entities import (
    EntityDataNotProvidedError,
    handle_delete_derived_entities,
)


def test__handle_delete_derived_entities_update_document() -> None:
    """
    Test the update of a document with derived entity information.

    This test ensures that when an entity is deleted, any references to it in related documents are
    also removed.

    Mocks
    -----
    - Mocks `get_documents` function to return a predefined document that needs to be updated.

    Asserts
    -------
    - The number of updated documents returned is 1.
    - The array of related entities no longer contains the deleted entity.
    """
    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="1234",
            type_name="m4i_data_entity",
            attributes=Attributes.from_dict({"name": "Data Entity Name"}),
        ),
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_domain",
        name="Domain Name",
        referenceablequalifiedname="domain_name",
        deriveddataentityguid=["1234", "3456"],
        deriveddataentity=["Data Entity Name", "Other Data Entity Name"],
    )

    with patch(
        __package__ + ".delete_derived_entities.get_documents",
        return_value=[document_to_update],
    ):
        updated_documents = handle_delete_derived_entities(message, Mock(), "test_index", {})

        assert len(updated_documents) == 1

        updated_document = updated_documents["2345"]
        assert updated_document.guid == "2345"
        assert updated_document.deriveddataentityguid == ["3456"]
        assert updated_document.deriveddataentity == ["Other Data Entity Name"]


def test__handle_update_derived_entities_no_old_value() -> None:
    """
    Test handling of messages with the old_value attribute missing.

    This test checks if the function raises an EntityDataNotProvidedError when the
    entity message lacks the 'old_value' attribute, which is essential for the update.

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
        handle_delete_derived_entities(message, Mock(), "test_index", {})
