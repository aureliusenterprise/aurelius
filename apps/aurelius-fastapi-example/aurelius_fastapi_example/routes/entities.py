from collections.abc import AsyncGenerator, Callable
from typing import Annotated
from uuid import UUID

import psycopg2
from aurelius_example import Entity
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy import func
from sqlalchemy.dialects.postgresql.ext import plainto_tsquery
from sqlmodel import Session, col, or_, select

from aurelius_fastapi_example.globals import LOGGER
from aurelius_fastapi_example.models import Envelope, FindAllQueryParams, PaginatedResponse
from aurelius_fastapi_example.providers import notifications, session, user_info

ENTITIES = APIRouter()


@ENTITIES.get(
    "/",
    summary="Get all entities",
    description="Retrieve all entities in the database.",
)
def find_all(
    params: Annotated[FindAllQueryParams, Depends()],
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Security(user_info)],
) -> PaginatedResponse[Entity]:
    """
    Retrieve all entities from the database with pagination support.

    Args:
        params (FindAllQueryParams): Query parameters for the find all endpoint.
        session (Session): The database session to use for the query.
        user_info (dict): Decoded user information from the authentication token.

    Returns:
        PaginatedResponse[Entity]: Paginated entities with total count.
    """
    LOGGER.info("User %s is retrieving entities", user_info.get("sub"))

    base_query = select(Entity)

    if params.search:
        tsquery = plainto_tsquery("english", params.search)
        search_filter = or_(
            col(Entity.name).op("@@")(tsquery),
            col(Entity.description).op("@@")(tsquery),
        )
        base_query = base_query.where(search_filter)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.exec(count_query).one()

    data_query = (
        base_query.order_by(func.coalesce(col(Entity.time_modified), col(Entity.time_created)).desc())
        .offset(params.skip)
        .limit(params.limit)
    )
    data = session.exec(data_query).all()

    return PaginatedResponse(data=data, total=total)


@ENTITIES.get(
    "/sse",
    summary="Stream entity changes",
    description="Real-time streaming endpoint for entity change notifications.",
    response_class=EventSourceResponse,
)
async def sse(
    notifications: Annotated[Callable[[], AsyncGenerator[psycopg2.extensions.Notify]], Depends(notifications)],
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Depends(user_info)],
) -> AsyncGenerator[ServerSentEvent]:
    """
    Stream server-sent events for entity changes.

    This endpoint streams real-time updates whenever entities are modified in the database.
    """
    LOGGER.info("User %s connected to SSE endpoint", user_info.get("sub"))

    try:
        async for notification in notifications():
            guid = UUID(notification.payload)

            envelope = Envelope(
                guid=guid,
                value=session.get(Entity, guid),
            )

            yield ServerSentEvent(
                event=notification.channel,
                data=envelope,
            )
    finally:
        LOGGER.info("User %s disconnected from SSE endpoint", user_info.get("sub"))


@ENTITIES.get(
    "/{guid}",
    summary="Get entity by GUID",
    description="Get an entity by its GUID.",
    responses={
        410: {"description": "Entity not found"},
    },
)
def find_one(
    guid: UUID,
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Security(user_info)],
) -> Entity:
    """
    Retrieve an entity by its GUID.

    Args:
        guid (UUID): The GUID of the entity to retrieve.
        session (Session): The database session to use for the query.
        user_info (dict): Decoded user information from the authentication token.

    Returns:
        Entity: The entity with the specified GUID.

    Raises:
        HTTPException: If the entity is not found, a 410 Gone error is raised.
    """
    LOGGER.info("User %s is retrieving entity with GUID %s", user_info.get("sub"), guid)

    if not (entity := session.get(Entity, guid)):
        raise HTTPException(status_code=410, detail="Entity not found")

    return entity


@ENTITIES.put(
    "/",
    summary="Create or update an entity",
    description="Create a new entity or update an existing entity.",
)
def create_or_update(
    entity: Entity,
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Security(user_info)],
) -> Entity:
    """
    Create a new entity or update an existing one.

    Args:
        entity (Entity): The entity to create or update.
        session (Session): The database session to use for the operation.
        user_info (dict): Decoded user information from the authentication token.

    Returns:
        Entity: The created or updated entity.
    """
    # Pydantic will not always correctly deserialize the guid field when validating from the request body, so we
    # re-validate it here to ensure it's in the correct format.
    if isinstance(entity.guid, str):
        entity = Entity.model_validate(entity.model_dump(mode="json"))

    LOGGER.info("User %s is creating or updating entity with GUID %s", user_info.get("sub"), entity.guid)

    session.merge(entity)
    session.commit()

    return session.get_one(Entity, entity.guid)


@ENTITIES.delete(
    "/{guid}",
    summary="Delete an entity",
    description="Delete an entity by its GUID.",
    responses={
        410: {"description": "Entity not found"},
    },
)
def delete(
    guid: UUID,
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Security(user_info)],
) -> None:
    """
    Delete an entity by its GUID.

    Args:
        guid (UUID): The GUID of the entity to delete.
        session (Session): The database session to use for the operation.
        user_info (dict): Decoded user information from the authentication token.

    Raises:
        HTTPException: If the entity is not found, a 410 Gone error is raised.
    """
    LOGGER.info("User %s is deleting entity with GUID %s", user_info.get("sub"), guid)

    if not (entity := session.get(Entity, guid)):
        raise HTTPException(status_code=410, detail="Entity not found")

    session.delete(entity)
    session.commit()
