from unittest.mock import Mock, patch

from m4i_atlas_core import (
    BusinessDataDomain,
    BusinessDataDomainAttributes,
    EntityAuditAction,
    M4IAttributes,
    ObjectId,
)

from flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType

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

    with (
        patch(
            __package__ + ".relationship_audit.get_current_document",
            return_value=current_document,
        ),
        patch(
            __package__ + ".relationship_audit.get_related_documents",
            return_value=related_documents,
        ),
        patch(
            __package__ + ".relationship_audit.get_child_documents",
            return_value=child_documents,
        ),
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

    with (
        patch(
            __package__ + ".relationship_audit.get_current_document",
            return_value=current_document,
        ),
        patch(
            __package__ + ".relationship_audit.get_related_documents",
            return_value=related_documents,
        ),
        patch(
            __package__ + ".relationship_audit.get_child_documents",
            return_value=child_documents,
        ),
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
