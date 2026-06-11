from m4i_analytics.shared.model.BaseModel import BaseModel


class DataContent(BaseModel):
    _fields = [
        ("start_date", int, False),
        ("end_date", int, False),
        ("id", str, False),
        ("data", dict, False),
    ]

    # Explicit type annotations for dynamically set attributes (helps pyright track them)
    start_date: int
    end_date: int
    id: str
    data: dict


# END DataContent
