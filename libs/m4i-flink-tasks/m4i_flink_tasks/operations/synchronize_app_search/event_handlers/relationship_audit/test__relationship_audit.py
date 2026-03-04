from unittest.mock import Mock, patch

from m4i_atlas_core import (
    BusinessDataDomain,
    BusinessDataDomainAttributes,
    BusinessDataEntity,
    BusinessDataEntityAttributes,
    EntityAuditAction,
    M4IAttributes,
    ObjectId,
)

from m4i_flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

from .relationship_audit import handle_relationship_audit


def test__handle_relationship_audit_inserted_relationship() -> None:
    """
    Test that the `handle_relationship_audit` function correctly handles added relationships.

    The function should update the documents with the new relationships and return the updated
    documents.

    Asserts
    -------
    - The updated documents contain the new relationships
    - The updated documents contain the correct breadcrumb information
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="2345",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
        new_value=BusinessDataDomain(
            guid="2345",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="data_domain",
                name="Data Domain",
                data_entity=[
                    ObjectId(
                        type_name="m4i_data_entity",
                        guid="1234",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Entity Name"}),
                    ),
                ],
            ),
        ),
        inserted_relationships={
            "data_entity": [
                ObjectId(
                    type_name="m4i_data_entity",
                    guid="1234",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Entity Name"}),
                ),
            ],
        },
        old_value=BusinessDataDomain(
            guid="2345",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="data_domain",
                name="Data Domain",
            ),
        ),
    )

    current_document = AppSearchDocument(
        guid="2345",
        typename="m4i_data_domain",
        name="Domain Name",
        referenceablequalifiedname="domain_name",
    )

    related_documents = [
        AppSearchDocument(
            guid="1234",
            typename="m4i_data_entity",
            name="Data Entity",
            referenceablequalifiedname="data_entity",
        ),
    ]

    child_documents = [
        AppSearchDocument(
            guid="1234",
            typename="m4i_data_entity",
            name="Data Entity",
            referenceablequalifiedname="data_entity",
        ),
    ]

    with patch(
        __package__ + ".relationship_audit.get_document",
        return_value=current_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=related_documents,
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=child_documents,
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert len(updated_documents) == 2

        updated_domain = updated_documents["2345"]
        assert updated_domain.deriveddataentity == ["Data Entity"]
        assert updated_domain.deriveddataentityguid == ["1234"]

        updated_entity = updated_documents["1234"]
        assert updated_entity.deriveddatadomain == ["Domain Name"]
        assert updated_entity.deriveddatadomainguid == ["2345"]
        assert updated_entity.breadcrumbguid == ["2345"]
        assert updated_entity.breadcrumbname == ["Domain Name"]
        assert updated_entity.breadcrumbtype == ["m4i_data_domain"]
        assert updated_entity.parentguid == "2345"


def test__handle_relationship_audit_deleted_relationship() -> None:
    """
    Test that the `handle_relationship_audit` function correctly handles deleted relationships.

    The function should update the documents with the removed relationships and return the updated
    documents.

    Asserts
    -------
    - The updated documents do not contain the removed relationships
    - The updated documents contain the correct breadcrumb information
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="2345",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
        old_value=BusinessDataDomain(
            guid="2345",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="data_domain",
                name="Data Domain",
                data_entity=[
                    ObjectId(
                        type_name="m4i_data_entity",
                        guid="1234",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Entity Name"}),
                    ),
                ],
            ),
        ),
        deleted_relationships={
            "data_entity": [
                ObjectId(
                    type_name="m4i_data_entity",
                    guid="1234",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Entity Name"}),
                ),
            ],
        },
        new_value=BusinessDataDomain(
            guid="2345",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="data_domain",
                name="Data Domain",
            ),
        ),
    )

    current_document = AppSearchDocument(
        guid="2345",
        typename="m4i_data_domain",
        name="Domain Name",
        referenceablequalifiedname="domain_name",
        deriveddataentity=["Data Entity"],
        deriveddataentityguid=["1234"],
    )

    related_documents = [
        AppSearchDocument(
            guid="1234",
            typename="m4i_data_entity",
            name="Data Entity",
            referenceablequalifiedname="data_entity",
            deriveddatadomain=["Domain Name"],
            deriveddatadomainguid=["2345"],
            breadcrumbguid=["2345"],
            breadcrumbname=["Domain Name"],
            breadcrumbtype=["m4i_data_domain"],
        ),
    ]

    child_documents = [
        AppSearchDocument(
            guid="1234",
            typename="m4i_data_entity",
            name="Data Entity",
            referenceablequalifiedname="data_entity",
            deriveddatadomain=["Domain Name"],
            deriveddatadomainguid=["2345"],
            breadcrumbguid=["2345"],
            breadcrumbname=["Domain Name"],
            breadcrumbtype=["m4i_data_domain"],
        ),
    ]

    with patch(
        __package__ + ".relationship_audit.get_document",
        return_value=current_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=related_documents,
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=child_documents,
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert len(updated_documents) == 2

        updated_domain = updated_documents["2345"]
        assert updated_domain.deriveddataentity == []
        assert updated_domain.deriveddataentityguid == []

        updated_entity = updated_documents["1234"]
        assert updated_entity.deriveddatadomain == []
        assert updated_entity.deriveddatadomainguid == []
        assert updated_entity.breadcrumbguid == []
        assert updated_entity.breadcrumbname == []
        assert updated_entity.breadcrumbtype == []


def test__handle_relationship_audit_replaced_parent_relationship() -> None:
    """
    Test that breadcrumbs are preserved when a parent relationship is being replaced.

    When a new parent is inserted in the same transaction as the old parent is removed,
    breadcrumbs should retain the old parent's values until the insertion event fully
    establishes the new parent relationship.

    Asserts
    -------
    - Breadcrumbs reflect the old parent exactly when a replacement is in progress
    """
    # Simulate an entity (child) losing its parent in a relationship audit
    # but having a new parent being inserted in the same message
    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="entity-1",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
        old_value=BusinessDataEntity(
            guid="entity-1",
            type_name="m4i_data_entity",
            attributes=BusinessDataEntityAttributes(
                qualified_name="test_entity",
                name="Test Entity",
            ),
        ),
        new_value=BusinessDataEntity(
            guid="entity-1",
            type_name="m4i_data_entity",
            attributes=BusinessDataEntityAttributes(
                qualified_name="test_entity",
                name="Test Entity",
            ),
        ),
        # No relationships in the flat deleted_relationships (parent guids are filtered out)
        deleted_relationships={},
        # New parent relationship being inserted
        inserted_relationships={
            "data_domain": [
                ObjectId(
                    type_name="m4i_data_domain",
                    guid="domain-new",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "New Domain"}),
                ),
            ],
        },
    )

    # Entity currently has breadcrumbs from old parent
    current_document = AppSearchDocument(
        guid="entity-1",
        typename="m4i_data_entity",
        name="Test Entity",
        referenceablequalifiedname="test_entity",
        breadcrumbguid=["domain-old"],
        breadcrumbname=["Old Domain"],
        breadcrumbtype=["m4i_data_domain"],
        parentguid="domain-old",
    )

    # New parent domain
    new_domain_document = AppSearchDocument(
        guid="domain-new",
        typename="m4i_data_domain",
        name="New Domain",
        referenceablequalifiedname="new_domain",
    )

    with patch(
        __package__ + ".relationship_audit.get_document",
        return_value=current_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=[new_domain_document],
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=[],
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert "entity-1" in updated_documents
        updated_entity = updated_documents["entity-1"]

        # The old parent's breadcrumbs are preserved until the new parent relationship
        # is fully established by a subsequent insertion event.
        assert updated_entity.breadcrumbguid == ["domain-old"]
        assert updated_entity.breadcrumbname == ["Old Domain"]
        assert updated_entity.breadcrumbtype == ["m4i_data_domain"]
        assert updated_entity.parentguid == "domain-old"


def test__handle_relationship_audit_new_parent_breadcrumbs_applied() -> None:
    """
    Test that breadcrumbs are updated to the new parent's chain when the new parent domain
    sends the insertion event linking the entity as a child.

    This represents the second step of a parent replacement: the new domain inserts the
    entity as a child, which triggers the breadcrumb update.

    Asserts
    -------
    - The entity's breadcrumbs reflect the new parent's chain (new domain's breadcrumbs + new domain)
    - parentguid is updated to the new domain
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="domain-new",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
        new_value=BusinessDataDomain(
            guid="domain-new",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="new_domain",
                name="New Domain",
                data_entity=[
                    ObjectId(
                        type_name="m4i_data_entity",
                        guid="entity-1",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "test_entity"}),
                    ),
                ],
            ),
        ),
        old_value=BusinessDataDomain(
            guid="domain-new",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes(
                qualified_name="new_domain",
                name="New Domain",
            ),
        ),
        inserted_relationships={
            "data_entity": [
                ObjectId(
                    type_name="m4i_data_entity",
                    guid="entity-1",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "test_entity"}),
                ),
            ],
        },
        deleted_relationships={},
    )

    # New domain has no breadcrumbs of its own (top-level)
    new_domain_document = AppSearchDocument(
        guid="domain-new",
        typename="m4i_data_domain",
        name="New Domain",
        referenceablequalifiedname="new_domain",
        breadcrumbguid=[],
        breadcrumbname=[],
        breadcrumbtype=[],
    )

    # The entity still has the old parent's breadcrumbs (preserved from the replacement event)
    entity_document = AppSearchDocument(
        guid="entity-1",
        typename="m4i_data_entity",
        name="Test Entity",
        referenceablequalifiedname="test_entity",
        breadcrumbguid=["domain-old"],
        breadcrumbname=["Old Domain"],
        breadcrumbtype=["m4i_data_domain"],
        parentguid="domain-old",
    )

    with patch(
        __package__ + ".relationship_audit.get_document",
        return_value=new_domain_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=[entity_document],
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=[],
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert "entity-1" in updated_documents
        updated_entity = updated_documents["entity-1"]

        # Breadcrumbs should now reflect the new domain
        assert updated_entity.breadcrumbguid == ["domain-new"]
        assert updated_entity.breadcrumbname == ["New Domain"]
        assert updated_entity.breadcrumbtype == ["m4i_data_domain"]
        assert updated_entity.parentguid == "domain-new"
