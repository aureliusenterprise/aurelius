from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import (
    AtlasPerson,
    AtlasPersonAttributes,
    BusinessDataEntity,
    BusinessDataEntityAttributes,
    EntityAuditAction,
    M4IAttributes,
    ObjectId,
)

from flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

from .entity_created import (
    EntityDataNotProvidedError,
    handle_entity_created,
)

QUERY_PATH = "flink_tasks.operations.synchronize_app_search.event_handlers.relationship_audit.relationship_audit"

def test__default_create_handler_with_complete_details() -> None:
    """
    Verify that `handle_entity_created` correctly processes an entity.

    Asserts:
    - The function produces one AppSearchDocument.
    - The AppSearchDocument's attributes correctly reflect the entity's details.
    """
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataEntity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataEntityAttributes.from_dict(
                {
                    "qualifiedName": "1234-test",
                    "name": "test",
                    "unmapped_attributes": {},
                },
            ),
        ),
    )

    with patch(__package__ + ".entity_created.get_related_documents", return_value=[]):
        result = handle_entity_created(entity_message, Mock(), "test_index", {})

        assert len(result) == 1

        document = result["1234"]

        assert document.id == "1234"
        assert document.guid == "1234"
        assert document.typename == "m4i_data_domain"
        assert document.name == "test"
        assert document.referenceablequalifiedname == "1234-test"


def test__create_person_handler_with_email() -> None:
    """
    Verify that `handle_entity_created` correctly processes a person entity.

    Asserts:
    - The function produces one AppSearchDocument.
    - The AppSearchDocument includes the `email` attribute, matching the entity's email.
    """
    entity_message = EntityMessage(
        type_name="m4i_person",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=AtlasPerson(
            guid="1234",
            type_name="m4i_person",
            attributes=AtlasPersonAttributes.from_dict(
                {
                    "qualifiedName": "1234-test",
                    "name": "test",
                    "email": "john.doe@example.com",
                },
            ),
        ),
    )

    with patch(__package__ + ".entity_created.get_related_documents", return_value=[]):
        result = handle_entity_created(entity_message, Mock(), "test_index", {})

        assert len(result) == 1

        document = result["1234"]

        assert document.id == "1234"
        assert document.guid == "1234"
        assert document.typename == "m4i_person"
        assert document.name == "test"
        assert document.referenceablequalifiedname == "1234-test"
        assert document.email == "john.doe@example.com"


def test__handle_entity_created_missing_entity_data() -> None:
    """
    Verify that `handle_entity_created` raises `EntityDataNotProvidedError` when no entity is given.

    Asserts:
    - `EntityDataNotProvidedError` is raised when the entity message lacks entity details.
    """
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
    )

    with pytest.raises(EntityDataNotProvidedError):
        handle_entity_created(entity_message, Mock(), "test_index", {})


def test__handle_entity_created_with_breadcrumbs() -> None:
    """
    Verify that handle_entity_created also creates breadcrumbs.

    Asserts
    - breadcrumbs are added
    """
    business_data_entity = BusinessDataEntity(
        guid="1111",
        type_name="m4i_data_entity",
        attributes=BusinessDataEntityAttributes.from_dict(
            {
                "qualifiedName": "test-data-entity",
                "name": "test entity",
                "unmapped_attributes": {"qualifiedName": "test-data-entity"},
            },
        ),
    )

    parent_ref = ObjectId(
        guid="2222",
        type_name="m4i_data_domain",
        unique_attributes=M4IAttributes(qualified_name="test object"),
    )

    business_data_entity.attributes.data_domain = [parent_ref]

    entity_message = EntityMessage(
        type_name="m4i_data_entity",
        guid="1111",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=business_data_entity,
        inserted_relationships={"dataDomain": [parent_ref]},
    )

    parent_document = AppSearchDocument(
        guid="2222",
        typename="m4i_data_domain",
        name="Domain Name",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["5678"],
        breadcrumbname=["Parent Data Domain Name"],
        breadcrumbtype=["m4i_data_domain"],
    )

    with (
        patch(__package__ + ".entity_created.get_related_documents", return_value=[parent_document]),
        patch(__package__ + ".entity_created.get_child_documents", return_value=[]),
    ):
        result = handle_entity_created(entity_message, Mock(), "test_index", {})

        assert len(result) == 2

        document = result["1111"]

        assert document.breadcrumbname == ["Parent Data Domain Name", "Domain Name"]
        assert document.breadcrumbguid == ["5678", "2222"]
        assert document.breadcrumbtype == ["m4i_data_domain", "m4i_data_domain"]
        assert document.parentguid == "2222"


def test__handle_entity_created_add_relations() -> None:
    """Verify that the created entity's relations are also added."""
    business_data_entity = BusinessDataEntity(
        guid="1111",
        type_name="m4i_data_entity",
        attributes=BusinessDataEntityAttributes.from_dict(
            {
                "qualifiedName": "test-data-entity",
                "name": "test entity",
                "unmapped_attributes": {},
            },
        ),
    )

    business_data_entity.attributes.data_domain = [
        ObjectId(
            guid="2222",
            type_name="m4i_data_domain",
            unique_attributes=M4IAttributes(
                qualified_name="My Data Domain",
                unmapped_attributes={},
            ),
        ),
    ]

    entity_message = EntityMessage(
        type_name="m4i_data_entity",
        guid="1111",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=business_data_entity,
        inserted_relationships={"dataDomain": business_data_entity.attributes.data_domain},
    )

    related_document = AppSearchDocument(
        guid="2222",
        typename="m4i_data_domain",
        name="My Data Domain",
        referenceablequalifiedname="entity_name",
        breadcrumbguid=["5678"],
        breadcrumbname=["Parent Data Domain Name"],
        breadcrumbtype=["m4i_data_domain"],
        parentguid="5678",
    )

    with (
        patch(__package__ + ".entity_created.get_related_documents", return_value=[related_document]),
        patch(__package__ + ".entity_created.get_child_documents", return_value=[]),
    ):
        result = handle_entity_created(entity_message, Mock(), "test_index", {})

        document = result["1111"]

        assert document.deriveddatadomainguid == ["2222"]
        assert document.deriveddatadomain == ["My Data Domain"]
        assert document.parentguid == "2222"

        related_document = result["2222"]

        assert related_document.deriveddataentityguid == ["1111"]
        assert related_document.deriveddataentity == ["test entity"]
        assert related_document.parentguid == "5678"


def test__handle_entity_created_multiple_relations() -> None:
    """Verify that multiple relations are created."""
    data_entity = BusinessDataEntity(
        guid="1111",
        type_name="m4i_data_entity",
        attributes=BusinessDataEntityAttributes.from_dict(
            {
                "qualifiedName": "1111-data-entity",
                "name": "Test Entity",
                "unmapped_attributes": {"qualifiedName": "1111-data-entity"},
            },
        ),
    )

    data_entity.attributes.data_domain = [
        ObjectId(
            guid="2222",
            type_name="m4i_data_domain",
            unique_attributes=M4IAttributes(
                qualified_name="2222-domain",
                unmapped_attributes={"name": "Test Data Domain"},
            ),
        ),
    ]

    data_entity.attributes.attributes = [
        ObjectId(
            guid="3333",
            type_name="m4i_data_attribute",
            unique_attributes=M4IAttributes(
                qualified_name="3333-attribute",
                unmapped_attributes={"name": "Test Data Attribute"},
            ),
        ),
    ]

    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="0000",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=data_entity,
        inserted_relationships={
            "dataDomain": data_entity.attributes.data_domain,
            "attributes": data_entity.attributes.attributes,
            },
    )

    related = [
        AppSearchDocument(
            guid="2222",
            typename="m4i_data_domain",
            name="Test Data Domain",
            referenceablequalifiedname="data_domain_name",
        ),
        AppSearchDocument(
            guid="3333",
            typename="m4i_data_attribute",
            name="Test Data Attribute",
            referenceablequalifiedname="data_attribute_name",
        ),
    ]

    with (
        patch(__package__ + ".entity_created.get_related_documents", return_value=related),
        patch(__package__ + ".entity_created.get_child_documents", return_value=[]),
    ):
        result = handle_entity_created(message, Mock(), "test_index", {})

        # Assert created entity's relations
        assert result["1111"].deriveddatadomainguid == ["2222"]
        assert result["1111"].deriveddatadomain == ["Test Data Domain"]
        assert result["1111"].deriveddataattributeguid == ["3333"]
        assert result["1111"].deriveddataattribute == ["Test Data Attribute"]
        # Assert relating back to the data entity
        assert result["2222"].deriveddataentityguid == ["1111"]
        assert result["2222"].deriveddataentity == ["Test Entity"]
        assert result["3333"].deriveddataentityguid == ["1111"]
        assert result["3333"].deriveddataentity == ["Test Entity"]
        # Assert breadcrumbs
        assert result["1111"].breadcrumbname == ["Test Data Domain"]
        assert result["1111"].breadcrumbguid == ["2222"]
        assert result["1111"].breadcrumbtype == ["m4i_data_domain"]

        assert result["2222"].breadcrumbname == []
        assert result["2222"].breadcrumbguid == []
        assert result["2222"].breadcrumbtype == []

        assert result["3333"].breadcrumbname == ["Test Data Domain", "Test Entity"]
        assert result["3333"].breadcrumbguid == ["2222", "1111"]
        assert result["3333"].breadcrumbtype == ["m4i_data_domain", "m4i_data_entity"]
