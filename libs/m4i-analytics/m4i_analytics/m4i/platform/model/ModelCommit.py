from enum import Enum

from m4i_analytics.shared.model.BaseModel import BaseModel


class ContentType(Enum):
    ARCHIMATE = "archimate"
    XML = "xml"
    JSON = "json"


# END ContentType


class ModelCommit(BaseModel):
    _fields = [
        ("parserName", str, False),
        ("projectName", str, False),
        ("branchName", str, False),
        ("module", str, False),
        ("modelId", str, False),
        ("contentType", str, False),
        ("comment", str, False),
        ("version", str, False),
        ("userid", str, False),
        ("taskId", str, False),
        ("intFileName", str, False),
        ("fileList", str, True),
    ]

    # Type declarations for pyright
    parserName: str
    projectName: str
    branchName: str
    module: str
    modelId: str
    contentType: str
    comment: str
    version: str
    userid: str
    taskId: str
    intFileName: str
    fileList: str


# END ModelCommit
