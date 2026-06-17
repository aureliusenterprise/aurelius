from m4i_analytics.shared.model.BaseModel import BaseModel


class UserRole(BaseModel):
    _fields = [
        ("userid", str, False),
        ("project", str, False),
        ("email", str, False),
        ("role_name", str, False),
        ("role_id", int, False),
    ]


# END Project
