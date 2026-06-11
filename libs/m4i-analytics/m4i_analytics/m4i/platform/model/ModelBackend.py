from m4i_analytics.shared.model.BaseModel import BaseModel


class ModelBackend(BaseModel):
    _fields = [
        ("file_list", str, True),
        ("parserName", str, False),
        ("projectName", str, False),
        ("branchName", str, False),
        ("userid", str, False),
        ("comment", str, False),
        ("contentType", str, False),
        ("taskId", str, False),
        ("version", str, False),
    ]


# END ModelBackend
