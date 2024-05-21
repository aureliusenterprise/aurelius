from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import (
    Attributes,
    BusinessDataDomain,
    BusinessDataDomainAttributes,
    BusinessDataEntity,
    BusinessDataEntityAttributes,
    Entity,
    EntityAuditAction,
)

from flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

from .update_derived_entities import (
    EntityDataNotProvidedError,
    handle_update_derived_entities,
)


def test__handle_update_derived_entities_update_document() -> None:
    """
    Test the update of a document with derived entity information.

    This test ensures that when the 'name' attribute of an entity is updated, the corresponding
    derived entity's name in a related document is also updated accordingly.

    Mocks
    -----
    - Mocks `get_documents` function to return a predefined document that needs to be updated.

    Asserts
    -------
    - The number of updated documents returned is 1.
    - The updated document's attributes are still correct.
    - The derived entity's name in the updated document is updated to the new name.
    """
    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataEntity(
            guid="1234",
            type_name="m4i_data_entity",
            attributes=BusinessDataEntityAttributes.from_dict({
                "name": "New Data Entity Name",
                "qualified_name": "1111",
            }),
        ),
        changed_attributes=["name"],
    )

    document_to_update = AppSearchDocument(
        guid="2345",
        typename="m4i_data_domain",
        name="Domain Name",
        referenceablequalifiedname="domain_name",
        deriveddataentityguid=["1234"],
        deriveddataentity=["Old Data Entity Name"],
    )

    with patch(
        __package__ + ".update_derived_entities.get_documents",
        return_value=[document_to_update],
    ):
        updated_documents = handle_update_derived_entities(message, Mock(), "test_index", {})

        assert len(updated_documents) == 1

        updated_document = updated_documents["2345"]
        assert updated_document.guid == "2345"
        assert updated_document.typename == "m4i_data_domain"
        assert updated_document.name == "Domain Name"
        assert updated_document.referenceablequalifiedname == "domain_name"
        assert updated_document.deriveddataentityguid == ["1234"]
        assert updated_document.deriveddataentity == ["New Data Entity Name"]


def test__handle_update_derived_entities_no_derived_entities() -> None:
    """
    Test handling of derived entities update when there are no derived entities to update.

    This test checks if the function returns an empty list when there are no derived entities
    related to the updated entity, as simulated by the mocked `get_documents` function.

    Mocks
    -----
    - Mocks `get_documents` function to return an empty list, simulating no derived entities.

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
            type_name="test_entity",
            attributes=BusinessDataDomainAttributes.from_dict({
                "name": "New Data Domain Name",
                "qualified_name": "1111",
            }),
        ),
        changed_attributes=["name"],
    )

    with patch(
        __package__ + ".update_derived_entities.get_documents",
        return_value=[],
    ):
        updated_documents = handle_update_derived_entities(message, Mock(), "test_index", {})

        assert len(updated_documents) == 0


def test__handle_update_derived_entities_no_name_update() -> None:
    """
    Test handling of derived entities update when there's no 'name' attribute update.

    This test verifies that the function returns an empty list when the updated message
    does not contain the 'name' attribute, indicating that no derived entity update is needed.

    Asserts
    -------
    - The function returns an empty list.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"description": "test"}),
        ),
        inserted_attributes=["description"],
    )

    updated_documents = handle_update_derived_entities(message, Mock(), "test_index", {})

    assert len(updated_documents) == 0


def test__handle_update_derived_entities_no_new_value() -> None:
    """
    Test handling of derived entities update when the new_value attribute is missing.

    This test checks if the function raises an EntityDataNotProvidedError when the
    entity message lacks the 'new_value' attribute, which is essential for the update.

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
        handle_update_derived_entities(message, Mock(), "test_index", {})
