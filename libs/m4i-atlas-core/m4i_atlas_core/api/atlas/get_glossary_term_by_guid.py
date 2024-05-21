from typing import Optional

from aiocache import cached

from ...entities import GlossaryTerm
from ..core import atlas_get

BASE_PATH = "v2/glossary/term"


@cached()
async def get_glossary_term_by_guid(guid: str, access_token: Optional[str] = None):

    path = f"{BASE_PATH}/{guid}"

    response: str = await atlas_get(path, access_token=access_token)

    return GlossaryTerm.from_json(response)
# END get_glossary_term_by_guid
