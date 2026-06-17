from m4i_analytics.shared.model.BaseModel import BaseModel


class UserSearch(BaseModel):
    _fields = [
        ("userName", str, False),
        ("email", str, False),
        ("firstName", str, False),
        ("lastName", str, False),
    ]


# END UserSearch
