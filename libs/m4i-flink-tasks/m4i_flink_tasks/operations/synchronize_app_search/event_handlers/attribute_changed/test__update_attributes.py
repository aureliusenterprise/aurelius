from unittest.mock import Mock

import pytest
from m4i_atlas_core import Attributes, BusinessDataDomain, BusinessDataDomainAttributes, Entity, EntityAuditAction

from m4i_flink_tasks import EntityMessage, EntityMessageType

from .update_attributes import (
    AppSearchDocumentNotFoundError,
    EntityDataNotProvidedError,
    handle_update_attributes,
)


@pytest.fixture()
def elasticsearch_response() -> Mock:
    """Return a mock Elasticsearch response."""
    mock_body = {
        "found": True,
        "_source": {
            "guid": "1234",
            "name": "test",
            "referenceablequalifiedname": "1234-test",
            "typename": "m4i_data_domain",
            "definition": "test",
            "email": "test",
        },
    }
    result = Mock()
    result.body = mock_body
    return result


@pytest.fixture()
def elasticsearch(elasticsearch_response: Mock) -> Mock:
    """Return a mock Elasticsearch instance."""
    result = Mock()
    result.get.return_value = elasticsearch_response
    return result


def test__update_with_valid_attributes(elasticsearch: Mock) -> None:
    """
    Test handle_update_attributes with valid attributes in the whitelist for update.

    This test verifies that when valid attributes (in the whitelist) are provided in the
    entity message, the function successfully updates these attributes in the Elasticsearch
    index and returns the updated document.

    Parameters
    ----------
    elasticsearch : Mock
        A mock Elasticsearch client instance.

    Asserts
    -------
    - The length of the returned document list is 1.
    - Each whitelisted attribute in the updated document matches the new value provided.
    - Elasticsearch 'get' method is called once with correct parameters.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=BusinessDataDomain(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=BusinessDataDomainAttributes.from_dict({
                "definition": "updated definition",
                "name": "new domain name",
                "qualified_name": "1111",
                }),
        ),
        inserted_attributes=["definition", "name"],
    )

    updated_docs = handle_update_attributes(message, elasticsearch, "test_index", {})

    assert len(updated_docs) == 1

    document = updated_docs["1234"]

    assert document.name == "new domain name"
    assert document.definition == "updated definition"

    elasticsearch.get.assert_called_once_with(index="test_index", id="1234")


def test__update_no_whitelisted_attributes(elasticsearch: Mock) -> None:
    """
    Test handle_update_attributes with no whitelisted attributes provided for update.

    This test checks that when the entity message does not contain any attributes from the
    whitelist, the function returns an empty list, indicating no update was performed.

    Parameters
    ----------
    elasticsearch : Mock
        A mock Elasticsearch client instance.

    Asserts
    -------
    - The returned document list is empty.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=Entity(
            guid="1234",
            type_name="test_entity",
            attributes=Attributes.from_dict({"non_whitelisted": "value"}),
        ),
        inserted_attributes=["non_whitelisted"],
        changed_attributes=[],
    )

    updated_docs = handle_update_attributes(message, elasticsearch, "test_index", {})

    assert len(updated_docs) == 0


def test__entity_message_without_new_value(elasticsearch: Mock) -> None:
    """
    Test handle_update_attributes with an entity message lacking new value.

    This test ensures that the function raises an EntityDataNotProvidedError when the
    entity message does not include new_value attribute, which is essential for the update.

    Parameters
    ----------
    elasticsearch : Mock
        A mock Elasticsearch client instance.

    Asserts
    -------
    - EntityDataNotProvidedError is raised.
    """
    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        inserted_attributes=["definition"],
    )

    with pytest.raises(EntityDataNotProvidedError):
        handle_update_attributes(message, elasticsearch, "test_index", {})


def test__entity_not_found_in_elasticsearch(elasticsearch: Mock) -> None:
    """
    Test handle_update_attributes for a non-existent entity in Elasticsearch.

    This test checks if the function raises an AppSearchDocumentNotFoundError when the
    entity corresponding to the provided GUID is not found in the Elasticsearch index.

    Parameters
    ----------
    elasticsearch : Mock
        A mock Elasticsearch client instance that simulates a 'not found' response.

    Asserts
    -------
    - AppSearchDocumentNotFoundError is raised.
    """
    elasticsearch.get.return_value.body = {"found": False}

    message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=Entity(
            guid="1234",
            type_name="test_entity",
            attributes=Attributes.from_dict({"non_whitelisted": "value"}),
        ),
        inserted_attributes=["definition"],
    )

    with pytest.raises(AppSearchDocumentNotFoundError):
        handle_update_attributes(message, elasticsearch, "test_index", {})
