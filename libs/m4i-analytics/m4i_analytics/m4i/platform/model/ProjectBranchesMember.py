from m4i_analytics.shared.model.BaseModel import BaseModel


class ProjectBranchesMember(BaseModel):
    _fields = [
        ("id", str, False),
        ("name", str, False),
        ("description", str, False),
        ("project_id", str, False),
        ("__v", int, False),
    ]


# END Project
