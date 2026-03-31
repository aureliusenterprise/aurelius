from functools import cache
from typing import Annotated

from fastapi import Depends

import aurelius_fastapi_example.models


@cache
def get_settings() -> aurelius_fastapi_example.models.Settings:
    """Return the application settings."""
    return aurelius_fastapi_example.models.Settings()  # type: ignore[settings are loaded from environment variables]


Settings = Annotated[aurelius_fastapi_example.models.Settings, Depends(get_settings)]
