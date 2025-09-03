from typing import List
from aiohttp import ClientResponseError
from m4i_atlas_core import create_entities, get_all_referred_entities

from ..meta import ExcelParserConfig
from .parse_json_to_atlas_entities import parse_json_to_atlas_entities
from .read_data_from_dictionary import read_data_from_dictionary
from ..meta import get_source
from ..entities.json.source.Source import *
from ..entities import T


async def get_ref_and_push(atlas_entities: List[T], with_referred_entities: bool, access_token: str):
    referred_entities = await get_all_referred_entities(
        atlas_entities
    ) if with_referred_entities else None

    # DEBUG: Print entities being sent
    print(f"DEBUG: Sending {len(atlas_entities)} entities to Atlas")
    for i, entity in enumerate(atlas_entities):
        print(f"  Entity {i}: {type(entity).__name__}")
        if hasattr(entity, 'guid'):
            print(f"    GUID: {entity.guid}")
        if hasattr(entity, 'attributes') and hasattr(entity.attributes, 'qualified_name'):
            print(f"    Qualified Name: {entity.attributes.qualified_name}")

    try:
      mutation_response = await create_entities(*atlas_entities, referred_entities=referred_entities, access_token=access_token)
      print(mutation_response)
    except ClientResponseError as e:
      print(f"ERROR: Failed to create entities. Status: {e.status}, Message: {e.message}")
      print(f"URL: {e.request_info.url}")
      raise


async def create_from_excel(
    *parser_configs: ExcelParserConfig,
    access_token: str,
    with_referred_entities: bool = False
):
    data = map(read_data_from_dictionary, parser_configs)

    atlas_entities_per_sheet = [
        parse_json_to_atlas_entities(sheet_data, sheet_config.parser_class)
        for sheet_data, sheet_config in zip(data, parser_configs)
    ]

    # Add Source Entity to Excel
    source_data, source_type = get_source()
    instance = source_type.from_dict(source_data)

    mutation_response = await create_entities(instance.convert_to_atlas(), access_token=access_token)
    print(mutation_response)

    for sheet_entities in atlas_entities_per_sheet:

        atlas_entities = list(sheet_entities)
        atlas_entities = [entity for entity in atlas_entities if entity is not None]
        print(f"Number of valid entities after filtering: {len(atlas_entities)}")

        if len(atlas_entities) > 0:
            try:
                await get_ref_and_push(atlas_entities, with_referred_entities, access_token)
            except ClientResponseError:
                print(f"Batch failed, trying individual entities...")
                for i, entity in enumerate(atlas_entities):
                    print(f"Trying entity {i}: {type(entity).__name__}")
                    try:
                        await get_ref_and_push([entity], with_referred_entities, access_token)
                        print(f"  SUCCESS: Entity {i}")
                    except ClientResponseError as e:
                        print(f"  FAILED: Entity {i} - Status: {e.status}, Message: {e.message}")

    # END LOOP
# END create_from_excel
