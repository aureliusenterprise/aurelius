import re
from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from aurelius_example import Entity
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.dialects.postgresql.ext import plainto_tsquery
from sqlmodel import Session, col, or_, select

from aurelius_fastapi_example.globals import LOGGER
from aurelius_fastapi_example.models import PaginationQueryParams
from aurelius_fastapi_example.providers import session, user_info

ENTITIES = APIRouter()


def sanitize_search_query(search: str | None) -> str | None:
    """
    Sanitize search query for PostgreSQL full-text search.

    Escapes special characters that could be interpreted as tsquery operators:
    - &: AND operator
    - |: OR operator
    - !: NOT operator
    - (: grouping
    - ): grouping
    - " : phrase matching

    Also removes control characters (ASCII 0x00-0x1F) to prevent potential issues.

    Args:
        search: The raw search query string.

    Returns:
        Sanitized search query or None if input is empty/whitespace only.
    """
    if not search:
        return None

    # Escape special tsquery operators by prefixing with backslash
    # Order matters - escape " first to avoid double-escaping
    sanitized = re.sub(r'(["&|!:()])', r"\\\1", search)

    # Remove null bytes and control characters (ASCII 0x00-0x1F)
    sanitized = re.sub(r"[\x00-\x1f]", "", sanitized)

    return sanitized if sanitized.strip() else None


@ENTITIES.get(
    "/",
    summary="Get all entities",
    description="Retrieve all entities in the database.",
)
def find_all(
    pagination: Annotated[PaginationQueryParams, Depends()],
    session: Annotated[Session, Depends(session)],
    user_info: Annotated[dict, Security(user_info)],
    search: str | None = None,
) -> Sequence[Entity]:
    """
    Retrieve all entities from the database.

    Args:
        pagination (PaginationQueryParams): Pagination parameters for the query.
        session (Session): The database session to use for the query.
        user_info (dict): Decoded user information from the authentication token.
        search (str | None): Optional search query to filter entities.

    Returns:
        Sequence[Entity]: All entities in the database.
    """
    LOGGER.info("User %s is retrieving entities", user_info.get("sub"))

    query = select(Entity).offset(pagination.skip).limit(pagination.limit)

    if search := sanitize_search_query(search):
        tsquery = plainto_tsquery("english", search)
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
