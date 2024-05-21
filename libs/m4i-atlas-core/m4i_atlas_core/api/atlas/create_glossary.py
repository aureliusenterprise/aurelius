from typing import Optional

from ...entities import Glossary
from ..core import atlas_post

PATH = "v2/glossary"


async def create_glossary(glossary: Glossary, access_token: Optional[str] = None):
    """
    API to create a glossary in Atlas.
    """

    response: str = await atlas_post(
        path=PATH,
        body=glossary.to_json(),
        access_token=access_token
    )

    return Glossary.from_json(response)
# END create_glossary
