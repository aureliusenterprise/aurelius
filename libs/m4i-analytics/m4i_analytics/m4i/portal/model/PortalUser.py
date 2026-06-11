from m4i_analytics.shared.model.BaseModel import BaseModel


class PortalUser(BaseModel):
    _fields = [
        ("username", str, False),
        ("email", str, False),
        ("first_name", str, False),
        ("last_name", str, False),
    ]


# END PortalUser
