from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from aurelius_example import Entity
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from aurelius_fastapi_example.models import PaginationQueryParams
from aurelius_fastapi_example.providers import session

ENTITIES = APIRouter()


@ENTITIES.get(
    "/",
    summary="Get all entities",
    description="Retrieve all entities in the database.",
)
def find_all(
    session: Annotated[Session, Depends(session)],
    pagination: Annotated[PaginationQueryParams, Depends()],
) -> Sequence[Entity]:
    """
    Retrieve all entities from the database.

    Args:
        session (Session): The database session to use for the query.
        pagination (PaginationQueryParams): Pagination parameters for the query.

    Returns:
        Sequence[Entity]: All entities in the database.
    """
    return session.exec(select(Entity).offset(pagination.skip).limit(pagination.limit)).all()


@ENTITIES.get(
    "/{guid}",
    summary="Get entity by GUID",
    description="Get an entity by its GUID.",
    responses={
        410: {"description": "Entity not found"},
    },
)
def find_one(guid: UUID, session: Annotated[Session, Depends(session)]) -> Entity:
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
    entity = session.get(Entity, guid)

    if not entity:
        raise HTTPException(status_code=410, detail="Entity not found")

    return entity


@ENTITIES.put(
    "/",
    summary="Create or update an entity",
    description="Create a new entity or update an existing entity.",
)
def create_or_update(entity: Entity, session: Annotated[Session, Depends(session)]) -> Entity:
    """
    Create a new entity or update an existing one.

    Args:
        entity (Entity): The entity to create or update.
        session (Session): The database session to use for the operation.

    Returns:
        Entity: The created or updated entity.
    """
    return session.merge(entity)


@ENTITIES.delete(
    "/{guid}",
    summary="Delete an entity",
    description="Delete an entity by its GUID.",
    responses={
        410: {"description": "Entity not found"},
    },
)
def delete(guid: UUID, session: Annotated[Session, Depends(session)]) -> None:
    """
    Delete an entity by its GUID.

    Args:
        guid (UUID): The GUID of the entity to delete.
        session (Session): The database session to use for the operation.

    Raises:
        HTTPException: If the entity is not found, a 410 Gone error is raised.
    """
    entity = session.get(Entity, guid)

    if not entity:
        raise HTTPException(status_code=410, detail="Entity not found")

    session.delete(entity)
