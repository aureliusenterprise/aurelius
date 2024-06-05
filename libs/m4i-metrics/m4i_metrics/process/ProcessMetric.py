from ..MetricCategory import MetricCategory
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

from .ActorAndRoleAssignmentMetric import ActorAndRoleAssignmentMetric
from .EventTriggersProcessMetric import EventTriggersProcessMetric
from .ProcessSequenceAndAbstractionMetric import ProcessSequenceAndAbstractionMetric
from .ExplicitControlFlowMetric import ExplicitControlFlowMetric
from .ProcessBoundariesMetric import ProcessBoundariesMetric


class ProcessMetric(MetricCategory):
    id = 'd749b53e-2fab-414c-a77d-99ede4dc72a0'
    metric_label = 'Process Metrics'

    metrics = [
        ActorAndRoleAssignmentMetric,
        EventTriggersProcessMetric,
        ProcessSequenceAndAbstractionMetric,
        ExplicitControlFlowMetric,
        ProcessBoundariesMetric,
    ]

    config = MetricConfig(**{
        'description': 'This metric aggregates the results of all metrics related to modeling patterns',
        'id_column': None,
        'data': {
            'metric': MetricColumnConfig(**{
                'displayName': 'Metric',
                'description': 'The name of the aggregated metric',
            }),
            'compliant': MetricColumnConfig(**{
                'displayName': '# of compliant elements',
                'description': 'The total amount of elements compliant with this metric'
            }),
            'non compliant': MetricColumnConfig(**{
                'displayName': '# of non-compliant elements',
                'description': 'The total amount of elements non-compliant with this metric'
            }),
            'exempted': MetricColumnConfig(**{
                'displayName': '# of exempt elements',
                'description': 'The total amount of elements exempt from this metric'
            })
        }
    })

# END ProcessMetric
