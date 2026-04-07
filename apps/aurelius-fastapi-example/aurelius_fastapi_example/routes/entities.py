from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from aurelius_example import Entity
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.dialects.postgresql.ext import plainto_tsquery
from sqlmodel import Session, col, or_, select

from aurelius_fastapi_example.globals import LOGGER
from aurelius_fastapi_example.models import FindAllQueryParams
from aurelius_fastapi_example.providers import session, user_info

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
) -> Sequence[Entity]:
    """
    Retrieve all entities from the database.

    Args:
        params (FindAllQueryParams): Query parameters for the find all endpoint.
        session (Session): The database session to use for the query.
        user_info (dict): Decoded user information from the authentication token.

    Returns:
        Sequence[Entity]: All entities in the database.
    """
    LOGGER.info("User %s is retrieving entities", user_info.get("sub"))

    query = select(Entity).offset(params.skip).limit(params.limit)

    if params.search:
        tsquery = plainto_tsquery("english", params.search)
        query = query.where(or_(col(Entity.name).op("@@")(tsquery), col(Entity.description).op("@@")(tsquery)))

    return session.exec(query).all()


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
