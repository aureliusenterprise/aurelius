from typing import Optional

from m4i_atlas_core import (register_atlas_entity_types, data_dictionary_entity_types,
                            get_entities_by_type_name, get_entity_by_guid)

from ...core.response import Response
from ...core.domains import Domains

from ...parse_entity import ParseEntity

from deepdiff import DeepSearch
from asyncio import as_completed


register_atlas_entity_types({
    **data_dictionary_entity_types
})


async def get_data_domains(access_token: Optional[str] = None) -> dict:
    """
    Get Data Domains in the required structure.

    {
    "total_number_of_domains": total_programs,
    "total_number_of_active_domains": active_programs,
    "domains": {
        'program_initials'{
            "name": program_name,
            "guid": "",
            "isActive": False,
            "totalNumberOfEntities": 0
        }
    }

    :param access_token:
    :return:dict
    """

    entity_headers = await get_entities_by_type_name(
        'm4i_data_domain', 10000, access_token=access_token
    )

    entities_async = [
        get_entity_by_guid(
            guid=header.guid,
            entity_type='m4i_data_domain',
            access_token=access_token
        )
        for header in entity_headers
    ]

    details = dict()
    known = []

    for domains_async in as_completed(entities_async):
        domain = await domains_async
        entity = ParseEntity(domain)

        if entity.get_dd_initials is not None:
            details = {
                **details,
                **entity.convert_to_details()
            }
            known.append(entity.get_dd_initials)

    # Build for non-existing data domains
    for program in set(list(Domains.__members__)) - set(known):
        details = {
            **details,
            **{
                str(program): {
                    "name": str(Domains[program].value),
                    "guid": "",
                    "isActive": False,
                    "totalNumberOfEntities": 0
                }
            }

        }

    # Summarize Data
    search = DeepSearch(details, 'isActive', verbose_level=2, case_sensitive=True)
    actives = len([v for k, v in search['matched_paths'].items() if v == True])

    return Response.from_dict({
        "total_number_of_domains": len(details),
        "total_number_of_active_domains": actives,
        "domains": details
    })
