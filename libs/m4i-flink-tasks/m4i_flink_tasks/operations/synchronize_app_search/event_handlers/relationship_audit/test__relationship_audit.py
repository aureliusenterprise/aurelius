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

    The function should rebuild the current document relationship fields from `new_value`.

    Asserts
    -------
    - The updated current document contains the new relationships
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

        assert len(updated_documents) == 1

        updated_domain = updated_documents["2345"]
        assert updated_domain.deriveddataentity == ["Data Entity"]
        assert updated_domain.deriveddataentityguid == ["1234"]


def test__handle_relationship_audit_deleted_relationship() -> None:
    """
    Test that the `handle_relationship_audit` function correctly handles deleted relationships.

    The function should rebuild the current document relationship fields from `new_value`.

    Asserts
    -------
    - The updated current document does not contain the removed relationships
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

        assert len(updated_documents) == 1

        updated_domain = updated_documents["2345"]
        assert updated_domain.deriveddataentity == []
        assert updated_domain.deriveddataentityguid == []


def test__handle_relationship_audit_replaced_parent_relationship() -> None:
    """
    Test that breadcrumbs are cleared when the current parent is removed.

    Asserts
    -------
    - Breadcrumbs are cleared when the entity has no parent in `new_value`
    """
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
                data_domain=[
                    ObjectId(
                        type_name="m4i_data_domain",
                        guid="domain-old",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Old Domain"}),
                    ),
                ],
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
        deleted_relationships={
            "data_domain": [
                ObjectId(
                    type_name="m4i_data_domain",
                    guid="domain-old",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "Old Domain"}),
                ),
            ],
        },
    )

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

    with patch(
        __package__ + ".relationship_audit.get_document",
        return_value=current_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=[],
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=[],
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert "entity-1" in updated_documents
        updated_entity = updated_documents["entity-1"]

        assert updated_entity.breadcrumbguid == []
        assert updated_entity.breadcrumbname == []
        assert updated_entity.breadcrumbtype == []
        assert updated_entity.parentguid is None


def test__handle_relationship_audit_new_parent_breadcrumbs_applied() -> None:
    """
    Test that breadcrumbs are updated to the new parent's chain when the entity gets a new parent.

    Asserts
    -------
    - The entity's breadcrumbs reflect the new parent's chain (new domain's breadcrumbs + new domain)
    - parentguid is updated to the new domain
    """
    message = EntityMessage(
        type_name="m4i_data_entity",
        guid="entity-1",
        original_event_type=EntityAuditAction.ENTITY_UPDATE,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
        new_value=BusinessDataEntity(
            guid="entity-1",
            type_name="m4i_data_entity",
            attributes=BusinessDataEntityAttributes(
                qualified_name="test_entity",
                name="Test Entity",
                data_domain=[
                    ObjectId(
                        type_name="m4i_data_domain",
                        guid="domain-new",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "new_domain"}),
                    ),
                ],
            ),
        ),
        old_value=BusinessDataEntity(
            guid="entity-1",
            type_name="m4i_data_entity",
            attributes=BusinessDataEntityAttributes(
                qualified_name="test_entity",
                name="Test Entity",
                data_domain=[
                    ObjectId(
                        type_name="m4i_data_domain",
                        guid="domain-old",
                        unique_attributes=M4IAttributes.from_dict({"qualifiedName": "old_domain"}),
                    ),
                ],
            ),
        ),
        inserted_relationships={
            "data_domain": [
                ObjectId(
                    type_name="m4i_data_domain",
                    guid="domain-new",
                    unique_attributes=M4IAttributes.from_dict({"qualifiedName": "new_domain"}),
                ),
            ],
        },
        deleted_relationships={},
    )

    new_domain_document = AppSearchDocument(
        guid="domain-new",
        typename="m4i_data_domain",
        name="New Domain",
        referenceablequalifiedname="new_domain",
        breadcrumbguid=[],
        breadcrumbname=[],
        breadcrumbtype=[],
    )

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
        side_effect=lambda guid, *_args: entity_document if guid == "entity-1" else new_domain_document,
    ), patch(
        __package__ + ".relationship_audit.get_related_documents",
        return_value=[],
    ), patch(
        __package__ + ".relationship_audit.get_child_documents",
        return_value=[],
    ):
        updated_documents = handle_relationship_audit(message, Mock(), "test_index", {})

        assert "entity-1" in updated_documents
        updated_entity = updated_documents["entity-1"]

        assert updated_entity.breadcrumbguid == ["domain-new"]
        assert updated_entity.breadcrumbname == ["New Domain"]
        assert updated_entity.breadcrumbtype == ["m4i_data_domain"]
        assert updated_entity.parentguid == "domain-new"
