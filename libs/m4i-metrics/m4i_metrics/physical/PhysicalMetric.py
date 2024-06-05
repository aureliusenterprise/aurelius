from ..MetricCategory import MetricCategory
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

from .EquipmentAssignedToFacilityMetric import EquipmentAssignedToFacilityMetric
from .FacilityRelationsMetric import FacilityRelationsMetric
from .DistributionNetworksMetric import DistributionNetworksMetric
from .MaterialFlowMetric import MaterialFlowMetric

class PhysicalMetric(MetricCategory):
    id = '6fe14887-e18e-42e6-9a96-deb97ee9a7af'
    metric_label = 'Physical Metrics'

    metrics = [
        EquipmentAssignedToFacilityMetric,
        FacilityRelationsMetric,
        DistributionNetworksMetric,
        MaterialFlowMetric,
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

# END PhysicalMetric
