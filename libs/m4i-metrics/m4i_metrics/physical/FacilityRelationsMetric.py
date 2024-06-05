import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from m4i_metrics.Metric import Metric
from m4i_metrics.MetricColumnConfig import MetricColumnConfig
from m4i_metrics.MetricConfig import MetricConfig

invalid_between_facilities_agg_config = MetricConfig(**{
    'description': 'These relationships are not aggregation/composition/realization or specialization between facilities',
    'id_column': 'id_rel',
    'data': {
        'id_rel': MetricColumnConfig(**{
            'displayName': 'Relationship ID',
            'description': 'The identifier of the relationship'
        }),
        'type_rel': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The type of the relationship'
        }),
        'name_src': MetricColumnConfig(**{
            'displayName': 'Source name',
            'description': 'The name of the source element of the relationship'
        }),
        'type_src': MetricColumnConfig(**{
            'displayName': 'Source type',
            'description': 'The type of the source element of the relationship'
        }),
        'name_tgt': MetricColumnConfig(**{
            'displayName': 'Target name',
            'description': 'The name of the target element of the relationship'
        }),
        'type_tgt': MetricColumnConfig(**{
            'displayName': 'Target type',
            'description': 'The type of the target element of the relationship'
        })
    }
})


class FacilityRelationsMetric(Metric):
    id = '9d782080-b992-4f4d-ab76-c58fb0ab52b8'
    label = 'Facility Relations'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        elems = elems[['id', 'name', 'type_']]
        rels = rels[['id', 'source', 'target', 'type_']]

        facility_elems = elems[(
            elems['type_'] == ElementType.FACILITY['typename'])]

        facility_agg = facility_elems.merge(
            rels, how='inner', left_on='id', right_on='source')
        facility_agg.rename(columns={'id_x': 'id_src', 'name': 'name_src',
                                     'type__x': 'type_src', 'id_y': 'id_rel', 'type__y': 'type_rel'}, inplace=True)
        facility_agg = facility_agg.merge(
            facility_elems, how='inner', left_on='target', right_on='id')
        facility_agg.rename(
            columns={'id': 'id_tgt', 'name': 'name_tgt', 'type_': 'type_tgt'}, inplace=True)
        facility_agg = facility_agg[['id_src', 'name_src', 'type_src',
                                     'id_rel', 'type_rel', 'id_tgt', 'name_tgt', 'type_tgt']]

        between_facilities_agg = facility_agg

        allRelsCount = len(between_facilities_agg)

        invalid_between_facilities_agg = between_facilities_agg[
            ~((between_facilities_agg['type_rel'] == RelationshipType.AGGREGATION['typename'])
              | (between_facilities_agg['type_rel'] == RelationshipType.COMPOSITION['typename'])
              | (between_facilities_agg['type_rel'] == RelationshipType.REALIZATION['typename'])
              # specialization between similar-type nodes is allowed always
              | (between_facilities_agg['type_rel'] == RelationshipType.SPECIALIZATION['typename']))]

        return {
            "Relationships between facilities": {
                "config": invalid_between_facilities_agg_config,
                "data": invalid_between_facilities_agg,
                "sample_size": allRelsCount,
                "type": "metric"
            }
        }
    # END of calculate


    def get_name(self):
        return 'FacilityRelationsMetric'
    # END get_name

# END FacilityRelationsMetric
