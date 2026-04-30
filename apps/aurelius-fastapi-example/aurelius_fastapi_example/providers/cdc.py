import asyncio
import contextlib
import queue
import threading
from collections.abc import AsyncGenerator, Callable
from functools import cache, partial
from types import TracebackType
from typing import Annotated, Self

import psycopg
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity, EntityNotification
from aurelius_sdk.events import Broadcaster
from aurelius_sdk.postgresql import PostgresListener
from fastapi import Depends, Request
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from aurelius_fastapi_example.globals import LOGGER
from aurelius_fastapi_example.models import Envelope

from .settings import Settings


class EntityNotificationBroadcaster(Broadcaster[Envelope[Entity]]):
    """Broadcaster that enriches entity notifications once before broadcasting them to subscribers."""

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings=settings)
        self._settings = settings
        self._connection: psycopg.Connection | None = None
        self._postgres_listener: PostgresListener | None = None
        self._listener_thread: threading.Thread | None = None
        self._listener_stop_event = threading.Event()

    def start(self) -> None:
        """Start the PostgreSQL listener and subscribe to receive notifications for broadcasting."""
        if self._is_running():
            return

        try:
            self._connection = psycopg.connect(
                autocommit=True,
                host=self._settings.database_host,
                port=self._settings.database_port,
                dbname=self._settings.database_name,
                user=self._settings.database_username,
                password=self._settings.database_password.get_secret_value(),
            )

            self._postgres_listener = PostgresListener(
                connection=self._connection,
                channel=PG_NOTIFY_ENTITY_CHANNEL,
            )

            self._postgres_listener.start()
            self._start_listener_thread()
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        """Stop the PostgreSQL listener and unsubscribe from notifications."""
        if self._postgres_listener:
            self._listener_stop_event.set()
            self._wake_listener_thread()
            self._stop_listener_thread()

            with contextlib.suppress(Exception):
                self._postgres_listener.stop()
            self._postgres_listener = None

        if self._connection:
            try:
                self._connection.close()
            except psycopg.Error as e:
                LOGGER.exception("Error closing PostgreSQL connection: %s", e)
            finally:
                self._connection = None

    def _is_running(self) -> bool:
        """Check if connection and listener are already initialized and active."""
        return (
            self._connection is not None
            and self._connection.closed == 0
            and self._postgres_listener is not None
            and self._postgres_listener.is_running
            and self._listener_thread is not None
            and self._listener_thread.is_alive()
        )

    def _start_listener_thread(self) -> None:
        """Start a background worker that consumes notifications and broadcasts them."""
        if self._listener_thread is not None and self._listener_thread.is_alive():
            return

        self._listener_stop_event.clear()
        self._listener_thread = threading.Thread(
            target=self._consume_notifications,
            name="entity-notification-broadcaster",
            daemon=True,
        )
        self._listener_thread.start()

    def _stop_listener_thread(self) -> None:
        """Join the background notification worker after stop has been signaled."""
        thread = self._listener_thread

        if thread is None:
            return

        thread.join(timeout=self._settings.cdc_shutdown_join_timeout)
        self._listener_thread = None

    def _wake_listener_thread(self) -> None:
        """Publish a wake-up notification so the listener thread can observe stop and exit promptly."""
        if self._connection is None:
            return

        try:
            with psycopg.connect(
                autocommit=True,
                host=self._settings.database_host,
                port=self._settings.database_port,
                dbname=self._settings.database_name,
                user=self._settings.database_username,
                password=self._settings.database_password.get_secret_value(),
            ) as wake_connection:
                wake_connection.execute("SELECT pg_notify(%s, %s);", (PG_NOTIFY_ENTITY_CHANNEL, "__stop__"))
        except psycopg.Error:
            LOGGER.debug("Failed to wake PostgreSQL listener thread during shutdown", exc_info=True)

    def _consume_notifications(self) -> None:
        """Consume listener notifications in the background to avoid blocking request handling."""
        listener = self._postgres_listener

        if listener is None:
            return

        try:
            for notify in listener:
                if self._listener_stop_event.is_set():
                    break

                self._process_notification(notify)
        except Exception:  # noqa: BLE001
            if not self._listener_stop_event.is_set():
                LOGGER.exception("Error while consuming PostgreSQL notifications")

    def _process_notification(self, notify: psycopg.Notify) -> None:
        if self.subscriber_count == 0:
            LOGGER.debug(
                "Skipping enrichment for notification %s because there are no subscribers",
                notify,
            )
            return
        try:
            notification = EntityNotification.model_validate_json(notify.payload)

            if notification.value is not None:
                # Re-parse the value field to ensure it's fully typed as an Entity model.
                notification.value = Entity.model_validate(notification.value.model_dump())

            envelope = Envelope(
                guid=notification.guid,
                op=notification.op,
                timestamp=notification.timestamp,
                value=notification.value,
            )

            self.broadcast(envelope)
        except (SQLAlchemyError, ValidationError):
            LOGGER.exception("Error broadcasting envelope for notification: %s", notify)

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
def get_broadcaster(*, settings: Settings) -> EntityNotificationBroadcaster:
    """Return a singleton Broadcaster instance for the application."""
    return EntityNotificationBroadcaster(settings=settings)


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
