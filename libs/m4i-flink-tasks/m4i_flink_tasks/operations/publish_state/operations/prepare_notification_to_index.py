import logging
from typing import Union

from m4i_atlas_core import AtlasChangeMessage
from pyflink.datastream import DataStream, OutputTag
from pyflink.datastream.functions import MapFunction

from m4i_flink_tasks import EntityVersion

NO_ENTITY_TAG = OutputTag("no_entity")


class PrepareNotificationToIndexFunction(MapFunction):
    """
    A custom `MapFunction` to prepare notifications for indexing.

    The function processes the validated input and transforms it into an `EntityVersion`
    object suitable for indexing.
    """

    def map(self, value: Union[AtlasChangeMessage, Exception]) -> Union[EntityVersion, Exception]:
        """
        Transform a ValidatedInput message into an EntityVersion object.

        Parameters
        ----------
        value : ValidatedInput
            The validated input message to be prepared for indexing.

        Returns
        -------
        EntityVersion
            The transformed message, ready for indexing.
        """
        logging.debug("PrepareNotificationToIndexFunction %s", value)

        if isinstance(value, Exception):
            return value

        msg_creation_time = value.msg_creation_time
        event_time = value.message.event_time
        entity = value.message.entity

        if entity is not None:
            entity.update_time = msg_creation_time

        if entity is None:
            logging.debug("Entity is required for indexing: %s", value)
            return ValueError("Entity is required for indexing")

        doc_id = f"{entity.guid}_{msg_creation_time}"

        return EntityVersion(
            entity,
            doc_id,
            event_time,
            msg_creation_time,
        )


class PrepareNotificationToIndex:
    """
    A class that sets up the Flink data stream for preparing notifications for indexing.

    This class initializes the data stream and applies the transformation logic using
    `PrapareNotificationToIndexFunction` to produce messages ready for indexing.

    Attributes
    ----------
    input_stream : DataStream
        The input stream of validated messages.
    main : DataStream
        The main output stream containing messages prepared for indexing.
    """

    def __init__(self, input_stream: DataStream) -> None:
        """
        Initialize the PrepareNotificationToIndex with an input data stream.

        Parameters
        ----------
        input_stream : DataStream
            The input stream of validated notifications.
        """
        self.input_stream = input_stream

        self.main = self.input_stream.map(PrepareNotificationToIndexFunction()).name(
            "index_preparation",
        )

        self.main = self.main.flat_map(
            lambda x: [x] if isinstance(x, EntityVersion) else [],
        )
