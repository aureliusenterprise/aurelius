from typing import Optional

from m4i_analytics.m4i.platform.model.DataContent import DataContent
from m4i_analytics.shared.model.BaseModel import BaseModel


class DataRetrieve(BaseModel):
    _fields = [
        ("project", str, False),
        ("branch", str, False),
        ("model_id", str, False),
        ("content", DataContent, True),
    ]

    # Explicit type annotations for dynamically set attributes (helps pyright track them)
    project: str
    branch: str
    model_id: str
    content: Optional[list[DataContent]]


# END DataRetrieve
