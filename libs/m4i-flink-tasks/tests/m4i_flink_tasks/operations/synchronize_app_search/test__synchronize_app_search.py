"""Tests for the SynchronizeAppSearchFunction class."""

import importlib
from typing import Tuple, Union, cast
from unittest.mock import Mock, patch

from m4i_atlas_core import Attributes, Entity, EntityAuditAction

from m4i_flink_tasks import AppSearchDocument, EntityMessage, EntityMessageType, SynchronizeAppSearchError

from m4i_flink_tasks.operations.synchronize_app_search.synchronize_app_search import (
    SynchronizeAppSearchFunction,
)


def test__synchronize_app_search_valid_input_event() -> None:
    """Test valid ENTITY_CREATED event produces AppSearchDocument tuple."""
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
        new_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"qualifiedName": "1234-test", "name": "test"}),
        ),
    )

    expected_document = AppSearchDocument(
        guid="1234", name="test", referenceablequalifiedname="1234-test", typename="m4i_data_domain"
    )

    func = SynchronizeAppSearchFunction(elastic_factory=Mock(), index_name="test-index")
    func.open(Mock())

    sync_module = importlib.import_module(
        "m4i_flink_tasks.operations.synchronize_app_search.synchronize_app_search"
    )

    with patch.object(
        sync_module,
        "EVENT_HANDLERS",
        new={EntityMessageType.ENTITY_CREATED: [Mock(return_value={"1234": expected_document})]},
    ):
        output = func.map(entity_message)

    assert len(output) == 1

    item = output[0]

    assert isinstance(item, tuple)

    guid, document = cast(Tuple[str, Union[AppSearchDocument, None]], item)

    assert guid == "1234"
    assert isinstance(document, AppSearchDocument)
    assert document.guid == "1234"


def test__synchronize_app_search_emit_tombstone_message() -> None:
    """Test ENTITY_DELETED event emits tombstone message (guid, None)."""
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_DELETE,
        event_type=EntityMessageType.ENTITY_DELETED,
        old_value=Entity(
            guid="1234",
            type_name="m4i_data_domain",
            attributes=Attributes.from_dict({"qualifiedName": "1234-test", "name": "test"}),
        ),
    )

    func = SynchronizeAppSearchFunction(elastic_factory=Mock(), index_name="test-index")
    func.open(Mock())

    sync_module = importlib.import_module(
        "m4i_flink_tasks.operations.synchronize_app_search.synchronize_app_search"
    )

    with patch.object(sync_module, "EVENT_HANDLERS", new={EntityMessageType.ENTITY_DELETED: []}):
        output = func.map(entity_message)

    assert len(output) == 1

    item = output[0]

    assert isinstance(item, tuple)

    guid, document = cast(Tuple[str, Union[AppSearchDocument, None]], item)

    assert guid == "1234"
    assert document is None


def test__synchronize_app_search_handle_processing_error() -> None:
    """Test processing error returns a list containing the SynchronizeAppSearchError."""
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
    )  # Entity details are missing

    func = SynchronizeAppSearchFunction(elastic_factory=Mock(), index_name="test-index")
    func.open(Mock())

    output = func.map(entity_message)

    assert len(output) == 1
    assert isinstance(output[0], SynchronizeAppSearchError)
