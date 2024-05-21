from typing import Optional

from aiocache import cached
from typing_extensions import Literal

from ...entities import Glossary
from ..core import atlas_get

PATH = "v2/glossary"


@cached()
async def get_glossary(
    limit: int = -1,
    offset: int = 0,
    sort: Literal['ASC', 'DESC'] = 'ASC',
    access_token: Optional[str] = None
):

    params = {
        "limit": limit,
        "offset": offset,
        "sort": sort
    }

    response: str = await atlas_get(
        path=PATH,
        params=params,
        access_token=access_token
    )

    glossary = Glossary.schema().loads(response, many=True)

    return glossary
# END get_glossary
