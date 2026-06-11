from enum import Enum

from m4i_analytics.shared.model.BaseModel import BaseModel


class TypeEnum(Enum):
    ARCHIMATE3 = "archimate3"


# END TypeEnum


class OperationEnum(Enum):
    CREATE_PROJECT = "create_project"
    RETRIEVE = "retrieve"
    COMMIT = "commit"
    MERGE = "merge"
    BRANCH_CLONE = "branch_clone"
    BRANCH_MERGE = "branch_merge"
    UPLOAD = "upload"


# END OperationEnum


class ModelProvenance(BaseModel):
    _fields = [
        ("type", str, False),
        ("id", str, False),
        ("project", str, False),
        ("branch", str, False),
        ("model_id", str, False),
        ("module", str, False),
        ("version", str, False),
        ("comment", str, False),
        ("start_date", int, False),
        ("end_date", int, False),
        ("start_user", str, False),
        ("end_user", str, False),
        ("min", str, False),
        ("derived_from_left", str, False),
        ("derived_from_right", str, False),
        ("operation", str, False),
    ]


# END ModelProvenance
