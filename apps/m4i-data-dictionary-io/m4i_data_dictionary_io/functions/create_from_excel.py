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

    mutation_response = await create_entities(*atlas_entities, referred_entities=referred_entities, access_token=access_token)
    print(mutation_response)


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

        if len(atlas_entities) > 0:
            try:
                await get_ref_and_push(atlas_entities, with_referred_entities, access_token)
            except ClientResponseError:
                for i in atlas_entities:
                    await get_ref_and_push([i], with_referred_entities, access_token)

    # END LOOP
# END create_from_excel
