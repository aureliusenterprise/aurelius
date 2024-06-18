import asyncio
import contextlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple, Callable, Union, cast

from aiohttp import ClientResponseError
from aiohttp.web import HTTPError
from m4i_atlas_core import (
    AtlasChangeMessage,
    ConfigStore,
    Entity,
    EntityAuditAction,
    ExistingEntityTypeException,
    UnknownEntityTypeException,
    data_dictionary_entity_types,
    get_entity_by_guid,
    register_atlas_entity_types,
)
from marshmallow import ValidationError
from pyflink.datastream import DataStream
from pyflink.datastream.functions import MapFunction, RuntimeContext

from m4i_flink_tasks.utils import ExponentialBackoff, retry
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError

# A type alias for a factory function that produces instances of KeycloakOpenID.
KeycloakFactory = Callable[[], KeycloakOpenID]


class GetEntityFunction(MapFunction):
    """
    A PyFlink map function that enriches an AtlasChangeMessage with entity details.

    If the entity is missing or there's an HTTP error during the enrichment, it outputs an
    error message to a side output. Utilizes a Keycloak instance to manage authentication tokens.

    Attributes
    ----------
    atlas_url : str
        The URL of the Apache Atlas API.
    keycloak_factory : KeycloakFactory
        A factory function to produce instances of KeycloakOpenID.
    credentials : tuple[str, str]
        A tuple containing the client_id and client_secret for authentication.
    keycloak : KeycloakOpenID
        The Keycloak instance used for token management.
    loop : asyncio.AbstractEventLoop
        The event loop used for asynchronous tasks.
    """

    def __init__(
        self,
        atlas_url: str,
        keycloak_factory: KeycloakFactory,
        credentials: Tuple[str, str],
    ) -> None:
        """
        Initialize the GetEntityFunction with a Keycloak factory and credentials.

        Parameters
        ----------
        atlas_url : str
            The URL of the Apache Atlas API.
        keycloak_factory : KeycloakFactory
            A factory function to produce instances of KeycloakOpenID.
        credentials : tuple[str, str]
            A tuple containing the client_id and client_secret for authentication.
        """
        self.atlas_url = atlas_url
        self.credentials = credentials
        self.keycloak_factory = keycloak_factory

        self._access_token = None
        self._token_expiration = datetime.now(tz=timezone.utc)

    def open(self, runtime_context: RuntimeContext) -> None:  # noqa: ARG002
        """Initialize the keycloak instance using the provided keycloak factory."""
        self.keycloak = self.keycloak_factory()
        self.loop = asyncio.new_event_loop()

        store = ConfigStore.get_instance()
        store.set("atlas.server.url", self.atlas_url)

        with contextlib.suppress(ExistingEntityTypeException):
            register_atlas_entity_types(data_dictionary_entity_types)

    def close(self) -> None:
        """Close the event loop."""
        self.loop.close()

    def map(self, value: str) -> Union[AtlasChangeMessage, Exception]:  # noqa: PLR0911
        """
        Process the incoming message and enrich it with entity details.

        Parameters
        ----------
        value : str
            The input message in JSON format.

        Returns
        -------
        AtlasChangeMessage
            If the message is successfully enriched.
        Exception
            If there's an error during processing.
        """
        try:
            # Deserialize the JSON string into a KafkaNotification object.
            # Using `cast` due to a known type hinting issue with schema.loads
            change_message = cast(
                AtlasChangeMessage,
                AtlasChangeMessage.schema().loads(value, many=False),
            )
        except ValidationError as e:
            logging.exception("Error deserializing message")
            return e

        logging.debug("Successfully deserialized message: %s", change_message)

        entity = change_message.message.entity

        if entity is None:
            logging.debug("No entity found in message: %s", change_message)
            return ValueError(f"No entity found in message. Value={value}")

        # Skipping types: m4i_source
        if entity.type_name == "m4i_source":
            logging.debug("Ignoring type: m4i_source, at %s", entity.guid)
            return ValueError("Ignoring type: m4i_source")

        if change_message.message.operation_type not in [
            EntityAuditAction.ENTITY_CREATE,
            EntityAuditAction.ENTITY_UPDATE,
            EntityAuditAction.ENTITY_DELETE,
        ]:
            logging.debug("Ignoring message type: %s", change_message.message.operation_type)
            return ValueError("Ignoring message type")

        if change_message.message.operation_type == EntityAuditAction.ENTITY_DELETE:
            return change_message

        try:
            entity_details = self.get_entity(entity.guid, entity.type_name)
        except (HTTPError, KeycloakError) as e:
            logging.exception("HTTP error during entity lookup")
            return RuntimeError(f"HTTP error during entity lookup: {e}")
        except UnknownEntityTypeException as e:
            logging.exception("Unknown type for entity: %s", change_message)
            return e
        except ClientResponseError as e:
            logging.exception("Can not find entity in atlas: %s", change_message)
            return RuntimeError(f"HTTP error during entity lookup: {e}")

        change_message.message.entity = entity_details

        logging.debug(
            "Successfully enriched change message. GUID = %s, TYPE = %s",
            entity_details.guid,
            entity_details.type_name,
        )

        return change_message

    @retry(retry_strategy=ExponentialBackoff(), catch=(HTTPError, KeycloakError, ClientResponseError), max_retries=2)
    def get_entity(self, guid: str, entity_type: str) -> Entity:
        """
        Get the entity details for the given GUID and entity type.

        Parameters
        ----------
        guid : str
            The GUID of the entity to fetch.
        entity_type : str
            The type of the entity to fetch.

        Returns
        -------
        Entity
            The entity details.
        """
        return self.loop.run_until_complete(
            get_entity_by_guid(
                guid=guid,
                entity_type=entity_type,
                access_token=self.access_token,
                cache_read=False,
            ),
        )

    @property
    def access_token(self) -> str:
        """
        Get the current access token using the Keycloak client.

        If the token has expired or is not set, a new token is fetched.

        The token is considered expired before its actual expiration time by a buffer to ensure that
        operations using the token do not fail due to a token that expires mid-operation. The buffer
        is set to 80% of the actual token's lifespan.

        Returns
        -------
        str
            The access token.
        """
        now = datetime.now(tz=timezone.utc)
        # If the token is expired or about to expire, fetch a new one
        if now > self._token_expiration or self._access_token is None:
            token_response = self.keycloak.token(*self.credentials)

            # Calculate the expiration time with some buffer (80% of the actual expiration)
            expires_in = int(token_response["expires_in"])
            self._token_expiration = now + timedelta(seconds=expires_in * 0.8)

            self._access_token = token_response["access_token"]

        return self._access_token


class GetEntity:
    """
    A class to handle the data stream and process it using the GetEntityFunction.

    This class initializes the main data stream, processes it, and handles errors by
    directing them to side outputs.

    Attributes
    ----------
    data_stream : DataStream
        The main data stream to be processed.
    main : DataStream
        The main data stream after processing with GetEntityFunction.
    """

    def __init__(
        self,
        data_stream: DataStream,
        atlas_url: str,
        keycloak_factory: KeycloakFactory,
        credentials: Tuple[str, str],
    ) -> None:
        """
        Initialize the GetEntity class with a given data stream.

        Parameters
        ----------
        data_stream : DataStream
            The input data stream to be processed.
        atlas_url : str
            The URL of the Apache Atlas API.
        keycloak_factory : KeycloakFactory
            A factory function to produce instances of KeycloakOpenID.
        """
        self.data_stream = data_stream

        self.main = self.data_stream.map(
            GetEntityFunction(atlas_url, keycloak_factory, credentials),
        ).name("enriched_entities")
