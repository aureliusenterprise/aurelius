import importlib
from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import (
    Attributes,
    BusinessDataDomain,
    BusinessDataDomainAttributes,
    Entity,
    EntityAuditAction,
)

from m4i_flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

# Deeply nested module path exceeds line limit - unavoidable without restructuring
from m4i_flink_tasks.operations.synchronize_app_search.event_handlers.attribute_changed.update_breadcrumbs import (  # noqa: E501
    EntityDataNotProvidedError,
    EntityNameNotFoundError,
    handle_update_breadcrumbs,
)

# Module reference for patch.object() - avoids long string-based path resolution
update_breadcrumbs_module = importlib.import_module(
    "m4i_flink_tasks.operations.synchronize_app_search.event_handlers.attribute_changed.update_breadcrumbs"
)

update_breadcrumbs_module = importlib.import_module(
    "m4i_flink_tasks.operations.synchronize_app_search.event_handlers.attribute_changed.update_breadcrumbs"
)


def test__handle_update_derived_entities_update_document() -> None:
    """
    Test the update of a document's breadcrumb information when an entity's name is updated.

    This test ensures that when an entity's 'name' attribute is updated, the corresponding
    name in the breadcrumb of a related document is also updated accordingly.

    Mocks
    -----
    - Mocks `get_documents` function to return a document that needs its breadcrumb updated.

    Asserts
    -------
    - The number of updated documents returned is 1.
    - The updated document's attributes are still correct.
    - The entity's name in the breadcrumb of the updated document is updated to the new name.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict(
                {"name": "New Data Domain Name", "qualified_name": "1111"}
            ),
        ),
        changed_attributes=["name"],
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234"],
        breadcrumbname=["Old Data Domain Name"],
    )

    with patch.object(update_breadcrumbs_module, "get_documents", return_value=[document_to_update]):
        updated_documents = handle_update_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 1

        updated_document = updated_documents["2345"]
        assert updated_document.guid == "2345"
        assert updated_document.typename == "m4i_data_entity"
        assert updated_document.name == "Entity Name"
        assert updated_document.referenceablequalifiedname == "entity_name"
        assert updated_document.breadcrumbguid == ["1234"]
        assert updated_document.breadcrumbname == ["New Data Domain Name"]


def test__handle_update_derived_entities_no_derived_entities() -> None:
    """
    Test handling of breadcrumb updates when there are no breadcrumb entities to update.

    This test checks if the function returns an empty list when there are no breadcrumb entities
    related to the updated entity, as simulated by the mocked `get_documents` function.

    Mocks
    -----
    - Mocks `get_documents` function to return an empty list, simulating no breadcrumb entities.

    Asserts
    -------
    - The function returns an empty list.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict(
                {"name": "Data Domain Name", "qualified_name": "1111"}
            ),
        ),
        changed_attributes=["name"],
    )

    with patch.object(update_breadcrumbs_module, "get_documents", return_value=[]):
        updated_documents = handle_update_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0


def test__handle_update_derived_entities_no_name_update() -> None:
    """
    Test handling of breadcrumb updates when there's no 'name' attribute update.

    This test verifies that the function returns an empty list when the updated message
    does not contain the 'name' attribute, indicating that no breadcrumb update is needed.

    Asserts
    -------
    - The function logs an error and does not update the malformed document.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=Entity(guid="1234", type_name="m4i_data_domain", attributes=Attributes.from_dict({})),
        changed_attributes=["name"],
    )

    with pytest.raises(EntityNameNotFoundError):
        handle_update_breadcrumbs(message, Mock(), "test_index", {})


def test__handle_update_derived_entities_no_new_value() -> None:
    """
    Test handling of breadcrumb updates when the new_value attribute is missing.

    This test checks if the function raises an EntityDataNotProvidedError when the
    entity message lacks the 'new_value' attribute, which is essential for the breadcrumb update.

    Asserts
    -------
    - EntityDataNotProvidedError is raised.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        changed_attributes=["name"],
    )

    with pytest.raises(EntityDataNotProvidedError):
        handle_update_breadcrumbs(message, Mock(), "test_index", {})


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
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict(
                {"name": "Data Domain Name", "qualified_name": "1111"}
            ),
        ),
        changed_attributes=["name"],
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234"],
        breadcrumbname=["Old Data Domain Name", "Old Data Domain Name"],
    )

    with patch.object(update_breadcrumbs_module, "get_documents", return_value=[document_to_update]):  # type: ignore[reportGeneralTypeIssues]
        with patch("logging.error") as mock_logger:
            updated_documents = handle_update_breadcrumbs(message, Mock(), "test_index", {})

            assert len(updated_documents) == 0

            mock_logger.assert_called_once_with(
                "Breadcrumb for document %s is malformed. Skipping document update.", document_to_update.guid
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
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict(
                {"name": "Data Domain Name", "qualified_name": "1111"}
            ),
        ),
        changed_attributes=["name"],
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["5678"],
        breadcrumbname=["Old Data Domain Name"],
    )

    with patch.object(update_breadcrumbs_module, "get_documents", return_value=[document_to_update]):
        updated_documents = handle_update_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0


def test__handle_update_breadcrumbs_name_already_correct() -> None:
    """
    Test handling of breadcrumb updates when the entity's name in the breadcrumb is already correct.

    This test checks if the function correctly skips the update when the entity's name in the
    document's breadcrumb is already up-to-date, avoiding unnecessary Elasticsearch writes.

    Mocks
    -----
    - Mocks `get_documents` to return a document with the correct entity name in its breadcrumb.

    Asserts
    -------
    - The function skips updating the document where the entity's name is already correct.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict(
                {"name": "Data Domain Name", "qualified_name": "1111"}
            ),
        ),
        changed_attributes=["name"],
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_entity",
        name="Entity Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["1234"],
        breadcrumbname=["Data Domain Name"],
    )

    with patch.object(update_breadcrumbs_module, "get_documents", return_value=[document_to_update]):
        updated_documents = handle_update_breadcrumbs(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0
