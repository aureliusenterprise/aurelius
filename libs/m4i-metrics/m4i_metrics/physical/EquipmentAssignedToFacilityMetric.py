import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from m4i_metrics.Metric import Metric
from m4i_metrics.MetricColumnConfig import MetricColumnConfig
from m4i_metrics.MetricConfig import MetricConfig

invalid_equipment_facilities_agg_config = MetricConfig(**{
    'description': 'These relationships are not assignment between equipment and facilities',
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


class EquipmentAssignedToFacilityMetric(Metric):
    id = '3bb32752-0527-4a81-b93a-8142dabee06b'
    label = 'Equipment Assigned to Facility'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        elems = elems[['id', 'name', 'type_']]
        rels = rels[['id', 'source', 'target', 'type_']]

        facility_elems = elems[(elems['type_'] == ElementType.FACILITY['typename'])
                               | (elems['type_'] == ElementType.EQUIPMENT['typename'])]

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

        equipment_facilities_agg = facility_agg[(
            (facility_agg['type_src'] == ElementType.EQUIPMENT['typename']) &
            (facility_agg['type_tgt'] == ElementType.FACILITY['typename']))
            | ((facility_agg['type_src'] == ElementType.FACILITY['typename']) &
               (facility_agg['type_tgt'] == ElementType.EQUIPMENT['typename']))]

        invalid_equipment_facilities_agg = equipment_facilities_agg[
            equipment_facilities_agg['type_rel'] != RelationshipType.ASSIGNMENT['typename']]
        invalid_equipment_facilities_agg.reset_index(drop=True, inplace=True)

        return {
            "Relationships between equipment and facilities": {
                "config": invalid_equipment_facilities_agg_config,
                "data": invalid_equipment_facilities_agg,
                "sample_size": len(equipment_facilities_agg.index),
                "type": "metric"
            }
        }
    # END of calculate


    def get_name(self):
        return 'EquipmentAssignedToFacilityMetric'
    # END get_name

# END EquipmentAssignedToFacilityMetric
