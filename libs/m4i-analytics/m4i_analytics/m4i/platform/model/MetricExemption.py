from m4i_analytics.shared.model.BaseModel import BaseModel


class MetricExemption(BaseModel):
    _fields = [
        ("branch", str, False),
        ("comment", str, False),
        ("concept_id", str, False),
        ("id", str, False),
        ("metric", str, False),
        ("project_id", str, False),
        ("version", int, False),
        ("userid", str, False),
        ("start_date", int, False),
    ]


# END MetricExemption
