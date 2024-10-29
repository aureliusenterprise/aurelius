from typing import Dict, Type, TypeVar

from .atlas import Entity

_atlas_entity_type_mapping: Dict[str, Type[Entity]] = {}


class ExistingEntityTypeException(Exception):
    """
    This exception is raised whenever the user attempts to register an entity type under an existing key
    """
# END ExistingEntityMappingException


class UnknownEntityTypeException(Exception):
    """
    This exception is raised whenever the user attempts to look up a non-existing entity type
    """
# END UnknownEntityMappingException


T = TypeVar('T', bound=Entity, covariant=True)


def register_atlas_entity_type(type_name: str, entity_type: Type[Entity]):
    """
    Registers the given `entity_type` under the given `type_name`.

    Registration makes the entity type available for the rest of the application as a plugin.

    Raises an `ExistingEntityTypeException` if there is already an entity type registered with the given `type_name`.
    """

    if type_name in _atlas_entity_type_mapping:
        raise ExistingEntityTypeException(
            f"Type name {type_name} already maps to an existing entity type"
        )
    # END IF

    _atlas_entity_type_mapping[type_name] = entity_type
# END register_atlas_entity_type


def register_atlas_entity_types(type_mapping: Dict[str, Type[Entity]]):
    """
    Registers every key-value pair in the given `type_mapping`.

    Registration makes the entity type available for the rest of the application as a plugin.

    Raises an `ExistingEntityTypeException` if there is already an entity type registered with a given name.
    """

    for type_name, entity_type in type_mapping.items():
        register_atlas_entity_type(type_name, entity_type)
    # END LOOP
# END register_atlas_entity_types


def get_entity_type_by_type_name(type_name: str) -> Type[Entity]:
    """
    Retrieves the entity type registered under the given `type_name` from the entity type registry.

    Raises an `UnknownEntityTypeException` if there is no entity type registered with the given `type_name`.
    """

    if type_name not in _atlas_entity_type_mapping:
        raise UnknownEntityTypeException(
            f"Type name {type_name} does not map to any known entities")
    # END IF

    return _atlas_entity_type_mapping.get(type_name, Entity)
# END get_entity_type_by_type_name
