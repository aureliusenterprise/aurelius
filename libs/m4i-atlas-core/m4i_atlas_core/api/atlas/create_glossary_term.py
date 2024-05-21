from typing import Optional

from ...entities import GlossaryTerm
from ..core import atlas_post

PATH = "v2/glossary/term"


async def create_glossary_term(term: GlossaryTerm, access_token: Optional[str] = None):
    """
    API to create a glossary term in Atlas.
    """

    response: str = await atlas_post(
        path=PATH,
        body=term.to_json(),
        access_token=access_token
    )

    return GlossaryTerm.from_json(response)
# END create_glossary_term
