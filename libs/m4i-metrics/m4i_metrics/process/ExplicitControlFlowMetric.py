import numpy as np
import pandas as pd

import m4i_metrics.config as config
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

trigger_flow_const_config = MetricConfig(**{
    'description': 'These elements connect to multiple in- or outgoing, flow or trigger relationships',
    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'type_': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'
        }),
        'rel_type': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The type of the connecting relationships'
        }),
        'direction': MetricColumnConfig(**{
            'displayName': 'Relationship direction',
            'description': 'The direction of the connecting relationships relative to the element'
        }),
        'cnt': MetricColumnConfig(**{
            'displayName': '# of relationships',
            'description': 'An absolute count of all relationships which belong to this group'
        })
    }
})


class ExplicitControlFlowMetric(Metric):
    id = '88dc7c6e-7f89-49ff-94e3-263b851bc5df'
    label = 'Explicit Control Flow'

    @staticmethod
    def calculate(model):

        # Create local copies of the model's nodes and edges dataframes so we can safely modify them
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])

        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        business_process = elems[elems.type_ ==
                                 ElementType.BUSINESS_PROCESS['typename']]
        business_function = elems[elems.type_ ==
                                  ElementType.BUSINESS_FUNCTION['typename']]
        business_interface = elems[elems.type_ ==
                                   ElementType.BUSINESS_INTERFACE['typename']]
        business_event = elems[elems.type_ ==
                               ElementType.BUSINESS_EVENT['typename']]
        application_process = elems[elems.type_ ==
                                    ElementType.APPLICATION_PROCESS['typename']]
        application_function = elems[elems.type_ ==
                                     ElementType.APPLICATION_FUNCTION['typename']]
        application_interface = elems[elems.type_ ==
                                      ElementType.APPLICATION_INTERFACE['typename']]
        application_event = elems[elems.type_ ==
                                  ElementType.APPLICATION_EVENT['typename']]

        behavior_ids = (
            business_process.id.to_list()
            + business_function.id.to_list()
            + business_interface.id.to_list()
            + business_event.id.to_list()
            + application_process.id.to_list()
            + application_function.id.to_list()
            + application_interface.id.to_list()
            + application_event.id.to_list()
        )

        trigger_rels = rels[rels.type_ ==
                            RelationshipType.TRIGGERING['typename']]

        flow_rels = rels[rels.type_ == RelationshipType.FLOW['typename']]

        # business processes and business functions must have a single inbound and outbound trigger or flow relationships
        trigger_source_agg = trigger_rels.groupby(
            by='source').size().rename('cnt').reset_index()
        trigger_source_agg.columns = [
            x if x == 'cnt' else 'elem_id' for x in trigger_source_agg.columns]
        trigger_source_agg['rel_type'] = 'trigger'
        trigger_source_agg['direction'] = 'outbound'
        trigger_target_agg = trigger_rels.groupby(
            by='target').size().rename('cnt').reset_index()
        trigger_target_agg.columns = [
            x if x == 'cnt' else 'elem_id' for x in trigger_target_agg.columns]
        trigger_target_agg['rel_type'] = 'trigger'
        trigger_target_agg['direction'] = 'inbound'
        flow_source_agg = flow_rels.groupby(
            by='source').size().rename('cnt').reset_index()
        flow_source_agg.columns = [
            x if x == 'cnt' else 'elem_id' for x in flow_source_agg.columns]
        flow_source_agg['rel_type'] = 'flow'
        flow_source_agg['direction'] = 'outbound'
        flow_target_agg = flow_rels.groupby(
            by='target').size().rename('cnt').reset_index()
        flow_target_agg.columns = [
            x if x == 'cnt' else 'elem_id' for x in flow_target_agg.columns]
        flow_target_agg['rel_type'] = 'flow'
        flow_target_agg['direction'] = 'inbound'
        data_df = pd.concat(
            [trigger_source_agg, trigger_target_agg, flow_source_agg, flow_target_agg], sort=False)
        data_df = data_df.merge(
            elems[['id', 'name', 'type_']], how='inner', left_on='elem_id', right_on='id')
        data_df['type'] = config.COMPLIANT_TAG
        data_df.loc[np.logical_and(data_df.cnt > 1, data_df.elem_id.isin(
            behavior_ids)), 'type'] = config.NON_COMPLIANT_TAG
        trigger_flow_const = data_df[data_df['type']
                                     == config.NON_COMPLIANT_TAG]

        return {
            "elements": {
                "config": trigger_flow_const_config,
                "data": trigger_flow_const,
                "sample_size": sum((len(elems.index), len(rels.index))),
                "type": "metric"
            }
        }
    # END of calculate

    def get_name(self):
        return 'ExplicitControlFlowMetric'
    # END get_name

# END ExplicitControlFlowMetric
