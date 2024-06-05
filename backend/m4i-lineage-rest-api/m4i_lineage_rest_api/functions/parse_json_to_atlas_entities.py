from typing import Iterable, Type

from ..lin_api.entity.ToAtlasConvertible import ToAtlasConvertible, T


def parse_json_to_atlas_entities(data: Iterable[dict], entity_type: Type[ToAtlasConvertible[T]]) -> Iterable[T]:
    entities = map(entity_type.from_dict, data)
    atlas_entities = map(entity_type.convert_to_atlas, entities)

    return atlas_entities
# END parse_json_to_atlas_entities
