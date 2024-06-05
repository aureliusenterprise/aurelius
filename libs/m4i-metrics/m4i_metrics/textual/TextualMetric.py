from m4i_metrics.MetricCategory import MetricCategory
from m4i_metrics.textual.LabelAndConceptDuplicationMetric import LabelAndConceptDuplicationMetric
from m4i_metrics.textual.ConceptLabelFormattingMetric import ConceptLabelFormattingMetric


from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig


class TextualMetric(MetricCategory):
    id =  'd260f268-3ff6-418b-ae70-6135bf21f63c'
    metric_label = 'Textual Metrics'
    metrics = [
        LabelAndConceptDuplicationMetric, 
        ConceptLabelFormattingMetric
    ]

    config = MetricConfig(**{
        'description': 'This metric aggregates the results of all metrics related to text',
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

# END TextualMetric
