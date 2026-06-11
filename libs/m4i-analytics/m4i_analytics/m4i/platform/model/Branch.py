from m4i_analytics.shared.model.BaseModel import BaseModel


class Branch(BaseModel):
    _fields = [
        ("id", str, False),
        ("description", str, False),
        ("name", str, False),
        ("project_id", str, False),
        ("protected", bool, False),
    ]


# END Branch
