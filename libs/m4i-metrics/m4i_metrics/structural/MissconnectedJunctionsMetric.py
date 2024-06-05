import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import \
    ElementType

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

invalid_junctions_direction_agg_config = MetricConfig(**{
    'description': 'These junctions have no outgoing or no incoming relations connected to them',
    'id_column': 'id_junction',
    'data': {
        'id_junction': MetricColumnConfig(**{
            'displayName': 'Junction ID',
            'description': 'The identifier of the junction'
        }),
        'type_junction': MetricColumnConfig(**{
            'displayName': 'Junction type',
            'description': 'The type of the junction'
        }),
        'incomingRelsCount': MetricColumnConfig(**{
            'displayName': 'Count of incoming relationships',
            'description': 'The number of  relationships incoming to the junction'
        }),
        'outgoingRelsCount': MetricColumnConfig(**{
            'displayName': 'Count of outgoing relationships',
            'description': 'The number of relationships outgoing from the junction'
        })
    }
})

invalid_junctions_type_agg_config = MetricConfig(**{
    'description': 'These junctions have more than one relationship type connected to them',
    'id_column': 'id_junction',
    'data': {
        'id_junction': MetricColumnConfig(**{
            'displayName': 'Junction ID',
            'description': 'The identifier of the junction'
        }),
        'type_junction': MetricColumnConfig(**{
            'displayName': 'Junction type',
            'description': 'The type of the junction'
        }),
        'relTypes': MetricColumnConfig(**{
            'displayName': 'Junction relationship types',
            'description': 'The types of relationships connected to the junction'
        })
    }
})


class MissconnectedJunctionsMetric(Metric):
    id  = 'd999cb70-1b0e-4e3f-b6bd-dcd8a27fe84f'
    label = 'Misconnected Junctions'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        elems = elems[['id', 'name', 'type_']]
        rels = rels[['id', 'source', 'target', 'type_']]

        elems['relTypes'] = elems['id'].apply(lambda x: set(
            rels[rels['source'] == x]['type_'].tolist() + rels[rels['target'] == x]['type_'].tolist()))
        elems['relTypesCount'] = elems['relTypes'].apply(lambda x: len(x))
        elems['relTypes'] = elems['relTypes'].apply(lambda x: ", ".join(x))
        elems['incomingRelsCount'] = elems['id'].apply(
            lambda x: len(rels[rels['target'] == x]))
        elems['outgoingRelsCount'] = elems['id'].apply(
            lambda x: len(rels[rels['source'] == x]))

        junctions_agg = elems[(elems['type_'] == ElementType.OR_JUNCTION['typename']) |
                              (elems['type_'] == ElementType.AND_JUNCTION['typename'])]

        junctions_agg.rename(columns={
                             'id': 'id_junction', 'name': 'name_junction', 'type_': 'type_junction'}, inplace=True)

        invalid_junctions_type_agg = junctions_agg[junctions_agg['relTypesCount'] > 1]
        invalid_junctions_type_agg = invalid_junctions_type_agg[
            ['id_junction', 'name_junction', 'type_junction', 'relTypes']]
        junctions_type_count = len(junctions_agg)

        invalid_junctions_direction_agg = junctions_agg[
            (junctions_agg['incomingRelsCount'] == 0) | (junctions_agg['outgoingRelsCount'] == 0)]
        invalid_junctions_direction_agg = invalid_junctions_direction_agg[
            ['id_junction', 'name_junction', 'type_junction', 'incomingRelsCount', 'outgoingRelsCount']]
        junctions_direction_count = len(junctions_agg)

        return {
            "Junction relation type similarity": {
                "config": invalid_junctions_type_agg_config,
                "data": invalid_junctions_type_agg,
                "sample_size": junctions_type_count,
                "type": 'metric'
            },
            "Junction relation direction count": {
                "config": invalid_junctions_direction_agg_config,
                "data": invalid_junctions_direction_agg,
                "sample_size": junctions_direction_count,
                "type": 'metric'
            }
        }
    # END of calculate


    def get_name(self):
        return 'MissconnectedJunctionsMetric'
    # END get_name

# END MissconnectedJunctionsMetric

