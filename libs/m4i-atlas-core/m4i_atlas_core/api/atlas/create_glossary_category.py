from typing import Optional

from ...entities import GlossaryCategory
from ..core import atlas_post

PATH = "v2/glossary/category"


async def create_glossary_category(category: GlossaryCategory, access_token: Optional[str] = None):
    """
    API to create a glossary category in Atlas.
    """

    response: str = await atlas_post(
        path=PATH,
        body=category.to_json(),
        access_token=access_token
    )

    return GlossaryCategory.from_json(response)
# END create_glossary_category
