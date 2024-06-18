from typing import Tuple, Union, cast
from unittest.mock import Mock, patch

import pytest
from m4i_atlas_core import Attributes, Entity, EntityAuditAction
from pyflink.datastream import StreamExecutionEnvironment

from m4i_flink_tasks import (
    AppSearchDocument,
    EntityMessage,
    EntityMessageType,
)

from .synchronize_app_search import SynchronizeAppSearch


@pytest.fixture()
def environment() -> StreamExecutionEnvironment:
    """
    Provide a StreamExecutionEnvironment for testing.

    This fixture initializes a Flink StreamExecutionEnvironment
    with a parallelism of 1 for consistent testing.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    return env


def test__synchronize_app_search_valid_input_event(environment: StreamExecutionEnvironment) -> None:
    """
    Test if `SynchronizeAppSearch` correctly processes a valid entity create event.

    Mocks
    -----
    - Mocks the `EVENT_HANDLERS` dictionary to return an empty list for the `ENTITY_CREATED` event.

    Asserts
    -------
    - The output should have a length of 1.
    - The output should be a tuple containing the GUID and an `AppSearchDocument` instance.
    - The `AppSearchDocument` should have the same GUID as the input message.
    """
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

    data_stream = environment.from_collection([entity_message])

    expected_document = AppSearchDocument(
        guid="1234",
        name="test",
        referenceablequalifiedname="1234-test",
        typename="m4i_data_domain",
    )

    with patch(
        __package__ + ".synchronize_app_search.EVENT_HANDLERS",
        new={EntityMessageType.ENTITY_CREATED: [Mock(return_value={"1234": expected_document})]},
    ):
        synchronize_app_search = SynchronizeAppSearch(data_stream, Mock, "test-index")
        output = list(synchronize_app_search.main.execute_and_collect())

    assert len(output) == 1

    item = output[0]

    assert isinstance(item, tuple)

    guid, document = cast(Tuple[str, Union[AppSearchDocument, None]], item)

    assert guid == "1234"
    assert isinstance(document, AppSearchDocument)
    assert document.guid == "1234"


def test__synchronize_app_search_emit_tombstone_message(
    environment: StreamExecutionEnvironment,
) -> None:
    """
    Test if `SynchronizeAppSearch` emits a tombstone message for an `ENTITY_DELETED` event.

    Mocks
    -----
    - Mocks the `EVENT_HANDLERS` dictionary to exclude all `ENTITY_DELETED` event handlers.

    Asserts
    -------
    - The output should have a length of 1.
    - The output should be a tuple containing the GUID and `None`.
    """
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

    data_stream = environment.from_collection([entity_message])

    with patch(
        __package__ + ".synchronize_app_search.EVENT_HANDLERS",
        new={EntityMessageType.ENTITY_DELETED: []},
    ):
        synchronize_app_search = SynchronizeAppSearch(
            data_stream,
            Mock,
            "test-index",
        )
        output = list(synchronize_app_search.main.execute_and_collect())

    assert len(output) == 1

    item = output[0]

    assert isinstance(item, tuple)

    guid, document = cast(Tuple[str, Union[AppSearchDocument, None]], item)

    assert guid == "1234"
    assert document is None


def test__synchronize_app_search_handle_processing_error(
    environment: StreamExecutionEnvironment,
) -> None:
    """
    Test if `SynchronizeAppSearch` correctly handles a processing error.

    Asserts
    -------
    - The output should have a length of 1.
    - The error should be a `SynchronizeAppSearchError` instance.
    """
    entity_message = EntityMessage(
        type_name="m4i_data_domain",
        guid="1234",
        original_event_type=EntityAuditAction.ENTITY_CREATE,
        event_type=EntityMessageType.ENTITY_CREATED,
    )  # Entity details are missing

    data_stream = environment.from_collection([entity_message])

    synchronize_app_search = SynchronizeAppSearch(data_stream, Mock, "test-index")
    output = list(synchronize_app_search.main.execute_and_collect())

    assert len(output) == 0
