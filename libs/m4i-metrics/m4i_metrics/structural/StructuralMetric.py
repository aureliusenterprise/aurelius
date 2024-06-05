from ..MetricCategory import MetricCategory
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

from .UseOfAssociationRelationsMetric import UseOfAssociationRelationsMetric
from .CycleDetectionMetric import CycleDetectionMetric
from .TreeStructuresMetric import TreeStructuresMetric
from .MissconnectedJunctionsMetric import MissconnectedJunctionsMetric
from .UnconnectedElementsMetric import UnconnectedElementsMetric
from .ElementsNotInAnyViewMetric import ElementsNotInAnyViewMetric
from .NestedElementsInViewMetric import NestedElementsInViewMetric

class StructuralMetric(MetricCategory):
    id = '8f0b40af-f490-44ea-887c-10bceb3aaecb'
    metric_label = 'Structural Metrics'
    metrics = [
        UseOfAssociationRelationsMetric,
        TreeStructuresMetric,
        MissconnectedJunctionsMetric,
        UnconnectedElementsMetric,
        ElementsNotInAnyViewMetric
    ]

    config = MetricConfig(**{
        'description': 'This metric aggregates the results of all metrics related to model structure',
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

# END StructuralMetric
