from m4i_analytics.shared.model.BaseModel import BaseModel


class PortalDashboards(BaseModel):
    _fields = [
        ("_id", str, False),
        ("publish_model", int, False),
        # , ('model_analytics', long, False)
    ]


# END PortalDashboards
