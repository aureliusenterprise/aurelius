from m4i_analytics.shared.model.BaseModel import BaseModel


class Model(BaseModel):
    _fields = [
        ("version", str, False),
        ("toBranch", str, False),
        ("id", str, False),
        ("parserName", str, False),
        ("projectName", str, False),
        ("fromBranchName", str, False),
        ("toBranchName", str, False),
        ("module", str, False),
        ("fromModelId", str, False),
        ("toModelId", str, False),
        ("userid", str, False),
        ("comment", str, False),
        ("contentType", str, False),
        ("file", str, False),
        ("addListLeft", str, True),
        ("addListRight", str, True),
        ("deleteListLeft", str, True),
        ("deleteListRight", str, True),
    ]


# END Model
