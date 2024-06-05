import numpy as np
import pandas as pd

import m4i_metrics.config as config
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

parent_non_compliant_elem_config = MetricConfig(**{
    'description': 'These process steps trigger other process steps at different abstraction levels in the model',
    'id_column': 'trigger_id',
    'data': {
        'trigger_id': MetricColumnConfig(**{
            'displayName': 'Trigger ID',
            'description': 'The identifier of the trigger relation connecting the source and target element'
        }),
        'name_source': MetricColumnConfig(**{
            'displayName': 'Source name',
            'description': 'The name of the source element'
        }),
        'type__source': MetricColumnConfig(**{
            'displayName': 'Source type',
            'description': 'The ArchiMate type of the source element'
        }),
        'name_target': MetricColumnConfig(**{
            'displayName': 'Target name',
            'description': 'The name of the target element'
        }),
        'type__target': MetricColumnConfig(**{
            'displayName': 'Target type',
            'description': 'The ArchiMate type of the target element'
        })
    }
})


class ProcessBoundariesMetric(Metric):
    id = 'e9dfaf0b-867c-434c-ab52-cd328dd61d06'
    label = 'Process Boundaries'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        business_process = elems[elems.type_ ==
                                 ElementType.BUSINESS_PROCESS['typename']]
        business_function = elems[elems.type_ ==
                                  ElementType.BUSINESS_FUNCTION['typename']]
        application_process = elems[elems.type_ ==
                                    ElementType.APPLICATION_PROCESS['typename']]
        application_function = elems[elems.type_ ==
                                     ElementType.APPLICATION_FUNCTION['typename']]

        behavior_ids = business_process.id.to_list()+business_function.id.to_list()\
            + application_process.id.to_list()+application_function.id.to_list()

        # missing here the junctions and the propagated trigger relations accross junctions
        trigger_rels = rels[np.logical_and(rels.type_ == RelationshipType.TRIGGERING['typename'],
                                           np.logical_and(rels.source.isin(behavior_ids), rels.target.isin(behavior_ids)))][['id', 'source', 'target']]
        composition_rels = rels[rels.type_ == RelationshipType.COMPOSITION['typename']][[
            'id', 'source', 'target']]
        aggregation_rels = rels[rels.type_ == RelationshipType.AGGREGATION['typename']][[
            'id', 'source', 'target']]
        comp_agg_rels = pd.concat([composition_rels, aggregation_rels])

        # C-> A
        parent_source = trigger_rels.merge(
            comp_agg_rels, how='left', left_on='source', right_on='target', suffixes=['_A', '_C'])
        parent_source['id_AC'] = parent_source['id_C']
        parent_source['id'] = parent_source['id_A']

        # B <- D
        parent_target = trigger_rels.merge(
            comp_agg_rels, how='left', on='target', suffixes=['_B', '_D'])
        parent_target['target_B'] = parent_target['target']
        parent_target['target_D'] = parent_target['target']
        parent_target['id_BD'] = parent_target['id_D']
        parent_target['id'] = parent_target['id_B']

        # trigger relation source and target must belong to the same sup process, thus, there must be a composition or
        # aggregation to the same concept
        parent_source_target = parent_source.merge(
            parent_target, how='inner', on='id')
        parent_source_target[config.METRIC_TAG] = parent_source_target.source_C == parent_source_target.source_D

        parent_non_compliant = parent_source_target[np.logical_and(np.logical_not(parent_source_target[config.METRIC_TAG]),
                                                                   np.logical_or(parent_source_target.source_C.notnull(), parent_source_target.source_D.notnull()))]

        parent_non_compliant_elem = parent_non_compliant[['id', 'source_A', 'target_B']].merge(
            elems[['id', 'name', 'type_']], how='inner', left_on='source_A', right_on='id')

        parent_non_compliant_elem = parent_non_compliant_elem.merge(
            elems[['id', 'name', 'type_']], how='inner', left_on='target_B', right_on='id', suffixes=['_source', '_target'])

        # rename id   -> id_target
        #        id_y -> id_source
        #        id_x -> trigger_id
        columns = list(parent_non_compliant_elem.columns)
        columns_ = []
        for item in columns:
            if item == 'id':
                columns_.append('id_target')
            elif item == 'id_y':
                columns_.append('id_source')
            elif item == 'id_x':
                columns_.append('trigger_id')
            else:
                columns_.append(item)
        parent_non_compliant_elem.columns = columns_

        return {
            "elements": {
                "config": parent_non_compliant_elem_config,
                "data": parent_non_compliant_elem,
                "sample_size": sum((len(elems.index), len(rels.index))),
                "type": 'metric'
            }
        }
    # END of calculate

    def get_name(self):
        return 'ProcessBoundariesMetric'
    # END get_name
# END ProcessBoundariesMetric