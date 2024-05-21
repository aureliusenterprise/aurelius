from typing import Optional

from aiocache import cached

from ...entities import ClassificationDef
from ..core import atlas_get

PATH = "v2/types/classificationdef/name/"


@cached()
async def get_classification_def(type_name: str, access_token: Optional[str] = None):

    response: str = await atlas_get(PATH+type_name, access_token=access_token)

    class_defs = ClassificationDef.from_json(response)

    return class_defs
# END get_classification_def
