import asyncio
import contextlib
import queue
from collections.abc import AsyncGenerator, Callable
from functools import cache, partial
from types import TracebackType
from typing import Annotated, Self

import psycopg2
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, EntityNotification
from aurelius_sdk.events import Broadcaster
from aurelius_sdk.postgresql import PostgresListener
from fastapi import Depends, Request
from pydantic import ValidationError

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


class EntityNotificationBroadcaster(Broadcaster[EntityNotification]):
    """Broadcaster that listens to PostgreSQL notifications and broadcasts them as EntityNotification objects."""

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings=settings)
        self._settings = settings
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

        self.broadcast(notification)

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
    settings: Settings,
) -> EntityNotificationBroadcaster:
    """Return a singleton Broadcaster instance for the application."""
    return EntityNotificationBroadcaster(settings=settings)


def notifications(
    broadcaster: Annotated[EntityNotificationBroadcaster, Depends(get_broadcaster)],
    request: Request,
    settings: Settings,
) -> Callable[[], AsyncGenerator[EntityNotification]]:
    """Return a factory that streams PostgreSQL notifications via the shared broadcaster."""

    async def listener() -> AsyncGenerator[EntityNotification]:
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
