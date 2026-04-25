import asyncio
import contextlib
import queue
from collections.abc import AsyncGenerator, Callable
from functools import cache, partial
from types import TracebackType
from typing import Annotated, Self

import psycopg2
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity, EntityNotification
from aurelius_sdk.events import Broadcaster
from aurelius_sdk.postgresql import PostgresListener
from fastapi import Depends, Request
from pydantic import ValidationError
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from aurelius_fastapi_example.globals import LOGGER
from aurelius_fastapi_example.models import Envelope

from .db import database
from .settings import Settings


class EntityNotificationBroadcaster(Broadcaster[Envelope[Entity]]):
    """Broadcaster that enriches entity notifications once before broadcasting them to subscribers."""

    def __init__(self, db_engine: Engine, settings: Settings) -> None:
        super().__init__(settings=settings)
        self._settings = settings
        self._db_engine = db_engine
        self._connection: psycopg2.extensions.connection | None = None
        self._postgres_listener: PostgresListener | None = None

    def start(self) -> None:
        """Start the PostgreSQL listener and subscribe to receive notifications for broadcasting."""
        if self._is_running():
            return

        try:
            self._connection = psycopg2.connect(
                host=self._settings.database_host,
                port=self._settings.database_port,
                dbname=self._settings.database_name,
                user=self._settings.database_username,
                password=self._settings.database_password.get_secret_value(),
            )

            self._connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

            self._postgres_listener = PostgresListener(
                connection=self._connection,
                channel=PG_NOTIFY_ENTITY_CHANNEL,
                settings=self._settings,
            )

            self._postgres_listener.subscribe(self._process_notification)
            self._postgres_listener.start()
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        """Stop the PostgreSQL listener and unsubscribe from notifications."""
        if self._postgres_listener:
            with contextlib.suppress(Exception):
                self._postgres_listener.unsubscribe(self._process_notification)
            with contextlib.suppress(Exception):
                self._postgres_listener.stop()
            self._postgres_listener = None

        if self._connection:
            try:
                self._connection.close()
            except psycopg2.Error as e:
                LOGGER.exception("Error closing PostgreSQL connection: %s", e)
            finally:
                self._connection = None

    def _is_running(self) -> bool:
        """Check if connection and listener are already initialized and active."""
        return self._connection is not None and self._connection.closed == 0 and self._postgres_listener is not None

    def _process_notification(self, notify: psycopg2.extensions.Notify) -> None:
        try:
            notification = EntityNotification.model_validate_json(notify.payload)
        except ValidationError:
            LOGGER.exception("Failed to parse notification payload: %s", notify.payload)
            return

        if self.subscriber_count == 0:
            LOGGER.debug(
                "Skipping enrichment for notification %s because there are no subscribers",
                notification,
            )
            return

        try:
            envelope = self._build_envelope(notification)
            self.broadcast(envelope)
        except (SQLAlchemyError, ValidationError):
            LOGGER.exception("Error broadcasting envelope for notification: %s", notification)

    def _build_envelope(self, notification: EntityNotification) -> Envelope[Entity]:
        """Resolve the entity once and wrap it in the SSE envelope shared by all subscribers."""
        value = None

        if notification.op != "DELETE":
            with Session(self._db_engine) as session:
                value = session.get(Entity, notification.guid)

            if value is None:
                LOGGER.debug(
                    "Entity %s was not found while enriching %s notification",
                    notification.guid,
                    notification.op,
                )

        return Envelope(
            guid=notification.guid,
            op=notification.op,
            timestamp=notification.timestamp,
            value=value,
        )

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.stop()


@cache
def get_broadcaster(
    *,
    db_engine: Annotated[Engine, Depends(database)],
    settings: Settings,
) -> EntityNotificationBroadcaster:
    """Return a singleton Broadcaster instance for the application."""
    return EntityNotificationBroadcaster(db_engine=db_engine, settings=settings)


def notifications(
    broadcaster: Annotated[EntityNotificationBroadcaster, Depends(get_broadcaster)],
    request: Request,
    settings: Settings,
) -> Callable[[], AsyncGenerator[Envelope[Entity]]]:
    """Return a factory that streams PostgreSQL notifications via the shared broadcaster."""

    async def listener() -> AsyncGenerator[Envelope[Entity]]:
        """Subscribe to the broadcaster and yield notifications until the client disconnects."""
        subscriber_queue = broadcaster.subscribe()

        try:
            while not (await request.is_disconnected()):
                try:
                    notify = await asyncio.to_thread(
                        partial(
                            subscriber_queue.get,
                            timeout=settings.cdc_disconnect_poll_timeout,
                        ),
                    )
                except asyncio.CancelledError:
                    LOGGER.debug("SSE notification listener cancelled")
                    raise
                except queue.Empty:
                    continue

                LOGGER.debug("SSE listener received notification: %s", notify)
                yield notify
        finally:
            broadcaster.unsubscribe(subscriber_queue)

    return listener
