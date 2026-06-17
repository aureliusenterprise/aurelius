from m4i_analytics.shared.model.BaseModel import BaseModel


class ProjectMember(BaseModel):
    _fields = [("_id", str, False), ("username", str, False), ("email", str, False)]


# END ProjectMember
