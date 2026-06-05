from m4i_analytics.m4i.platform.model.Permission import Permission
from m4i_analytics.m4i.platform.model.PortalDashboards import PortalDashboards
from m4i_analytics.m4i.platform.model.ProjectMember import ProjectMember
from m4i_analytics.shared.model.BaseModel import BaseModel


class ProjectMetadata(BaseModel):
    _fields = [
        ("last_updated", int, False),
        ("id", str, False),
        ("type_", str, False),
        ("owner", str, False),
        ("name", str, False),
        ("committer", ProjectMember, False),
        ("documentation", str, False),
        ("subscription", str, False),
        ("expiration_date", int, False),
        ("start_date", int, False),
        ("end_date", int, False),
        ("derived_from", str, False),
        ("project_id", str, False),
        ("normalized_name", str, False),
        ("last_update_message", str, False),
        ("rights", Permission, True),
        ("portal", PortalDashboards, False),
        ("__v", int, False),
    ]


# END Project
