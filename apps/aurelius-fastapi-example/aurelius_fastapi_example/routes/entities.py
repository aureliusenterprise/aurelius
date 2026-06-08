from collections.abc import AsyncGenerator, Callable
from typing import Annotated
from uuid import UUID

from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity
from fastapi import APIRouter, Depends, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy import func
from sqlalchemy.dialects.postgresql.ext import plainto_tsquery
from sqlmodel import Session, col, or_, select

from aurelius_fastapi_example.models import Envelope, FindAllQueryParams, PaginatedResponse
from aurelius_fastapi_example.providers import notifications, require_auth, session

ENTITIES = APIRouter(dependencies=[require_auth])


@ENTITIES.get(
    "/",
    summary="Get all entities",
    description="Retrieve all entities in the database.",
)
def find_all(
    params: Annotated[FindAllQueryParams, Depends()],
    session: Annotated[Session, Depends(session)],
) -> PaginatedResponse[Entity]:
    """
    Retrieve all entities from the database with pagination support.

    Args:
        params (FindAllQueryParams): Query parameters for the find all endpoint.
        session (Session): The database session to use for the query.

    Returns:
        PaginatedResponse[Entity]: Paginated entities with total count.
    """
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
    notifications: Annotated[Callable[[], AsyncGenerator[Envelope[Entity]]], Depends(notifications)],
) -> AsyncGenerator[ServerSentEvent]:
    """
    Stream server-sent events for entity changes.

    This endpoint streams real-time updates whenever entities are modified in the database.
    """
    async for envelope in notifications():
        yield ServerSentEvent(event=PG_NOTIFY_ENTITY_CHANNEL, data=envelope)


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
) -> Entity:
    """
    Retrieve an entity by its GUID.

    Args:
        guid (UUID): The GUID of the entity to retrieve.
        session (Session): The database session to use for the query.

    Returns:
        Entity: The entity with the specified GUID.

    Raises:
        HTTPException: If the entity is not found, a 410 Gone error is raised.
    """
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
) -> Entity:
    """
    Create a new entity or update an existing one.

    Args:
        entity (Entity): The entity to create or update.
        session (Session): The database session to use for the operation.

    Returns:
        Entity: The created or updated entity.
    """
    # Pydantic will not always correctly deserialize the guid field when validating from the request body, so we
    # re-validate it here to ensure it's in the correct format.
    if isinstance(entity.guid, str):
        entity = Entity.model_validate(entity.model_dump(mode="json"))

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
) -> None:
    """
    Delete an entity by its GUID.

    Args:
        guid (UUID): The GUID of the entity to delete.
        session (Session): The database session to use for the operation.

    Raises:
        HTTPException: If the entity is not found, a 410 Gone error is raised.
    """
    if not (entity := session.get(Entity, guid)):
        raise HTTPException(status_code=410, detail="Entity not found")

    session.delete(entity)
    session.commit()
