from m4i_analytics.m4i.platform.model.ProjectMember import ProjectMember
from m4i_analytics.shared.model.BaseModel import BaseModel


class Permission(BaseModel):
    _fields = [
        ("_id", str, False),
        ("permission", str, False),
        ("users", ProjectMember, True),
    ]


# END Permission
