import pytest
from m4i_atlas_core import (
    AtlasChangeMessage,
    AtlasChangeMessageBody,
    AtlasChangeMessageVersion,
    Entity,
    EntityAuditAction,
    EntityNotificationType,
)
from pyflink.datastream import StreamExecutionEnvironment

from flink_tasks import KafkaNotification


@pytest.fixture()
def environment() -> StreamExecutionEnvironment:
    """
    Pytest fixture to provide a StreamExecutionEnvironment for testing.

    Returns
    -------
    StreamExecutionEnvironment
        An instance of Flink's StreamExecutionEnvironment.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    return env


@pytest.fixture()
def event() -> KafkaNotification:
    """
    Pytest fixture to provide a sample KafkaNotification event for testing.

    Returns
    -------
    KafkaNotification
        A sample KafkaNotification object.
    """
    return KafkaNotification(
        msg_creation_time=1,
        event_time=1,
        atlas_entity_audit={},
        kafka_notification=AtlasChangeMessage(
            version=AtlasChangeMessageVersion(
                version="1",
                version_parts=[],
            ),
            msg_compression_kind="",
            msg_split_idx=1,
            msg_split_count=1,
            msg_source_ip="localhost",
            msg_created_by="test",
            msg_creation_time=1,
            message=AtlasChangeMessageBody(
                event_time=1,
                operation_type=EntityAuditAction.ENTITY_CREATE,
                type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
                entity=Entity(guid="1234"),
                relationship=None,
            ),
            spooled=False,
        ),
    )
