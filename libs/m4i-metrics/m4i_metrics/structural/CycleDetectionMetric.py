import networkx as nx
import numpy as np
import pandas as pd

from m4i_analytics.graphs.GraphUtils import GraphUtils
from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
    ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import \
    RelationshipType

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

cycles_config = MetricConfig(**{
    'description': 'The set of elements connected via aggretation or composition relationships that form a cycle.',
    'id_column': None,
    'data': {
        'elements_id': MetricColumnConfig(**{
            'displayName': 'Elements ID',
            'description': 'The identifiers of the elements in the cycle.'
        }),
        'cycle_size': MetricColumnConfig(**{
            'displayName': 'Cycle Size',
            'description': 'The number of elements in the cycle.'
        }),
        'element_types': MetricColumnConfig(**{
            'displayName': 'Element Types',
            'description': 'The ArchiMate types of the elements in the cycle.'
        }),
        'rel_types': MetricColumnConfig(**{
            'displayName': 'Relation Types',
            'description': 'The ArchiMate type of the connecting relationships between elements in cycle.'
        }),
    }
})


class CycleDetectionMetric(Metric):
    '''
    Determines if their Exists Cycles in Hierarchical Relationships 
    Determines if their Exists Cycles for Specialization Relationships 
    '''
    id = 'f77bcf19-0141-4950-ae98-0ba919398d7a'
    label = 'Cycle Detection Metric'

    @staticmethod
    def calculate(model):
        # sliced model for hierarchical relationships
        model_sliced = ArchimateUtils.sliceByEdgeType(
            model, [RelationshipType.COMPOSITION, RelationshipType.AGGREGATION])

        # sliced model for specialization relationships
        model2_sliced = ArchimateUtils.sliceByEdgeType(
            model, [RelationshipType.SPECIALIZATION])

        # convert model to graph to apply NetworkX cycle finding algorithm
        # - algorithm applies to a directed graph representation of model
        # - includes self-loop
        G_sliced = GraphUtils.toNXGraph(model_sliced)
        cycles_list = list(nx.simple_cycles(G_sliced))

        G2_sliced = GraphUtils.toNXGraph(model2_sliced)
        cycles2_list = list(nx.simple_cycles(G2_sliced))

        # expand cycle list with attributes of elements & relationships
        rel_types = []
        element_types = []
        for nodes in cycles_list:
            # get the relationship types present between elements in the cycle
            edges_temp = list(G_sliced.edges(nodes, data=True))
            filtered_edges_temp = [x for x in edges_temp if (
                x[0] in nodes and x[1] in nodes)]
            rel_types.append(', '.join({i[2]['type_name']
                                        for i in filtered_edges_temp}))

            # get the unique element types present in the cycle
            element_types.append(
                ', '.join({G_sliced.nodes[i]['type_name'] for i in nodes}))
        # END LOOP

        # expand cycle list with attributes of elements & relationships
        rel_types2 = []
        element_types2 = []
        for nodes in cycles2_list:
            # get the relationship types present between elements in the cycle
            edges_temp = list(G2_sliced.edges(nodes, data=True))
            filtered_edges_temp = [x for x in edges_temp if (
                x[0] in nodes and x[1] in nodes)]
            rel_types2.append(
                ', '.join({i[2]['type_name'] for i in filtered_edges_temp}))

            # get the unique element types present in the cycle
            element_types2.append(
                ', '.join({G2_sliced.nodes[i]['type_name'] for i in nodes}))
        # END LOOP

        cycles = pd.DataFrame({'elements_id': [', '.join(i) for i in cycles_list],
                               'cycle_size': [len(i) for i in cycles_list],
                               'element_types': element_types,
                               'rel_types': rel_types})
        cycles2 = pd.DataFrame({'elements_id': [', '.join(i) for i in cycles2_list],
                                'cycle_size': [len(i) for i in cycles2_list],
                                'element_types': element_types2,
                                'rel_types': rel_types2})

        return {
            "detected cycles": {
                "config": cycles_config,
                "data": cycles,
                "sample_size": len(model.nodes)+len(model.edges)+len(model.views),
                "type": 'metric'
            },
            "detected specialization cycles": {
                "config": cycles_config,
                "data": cycles2,
                "sample_size": len(model.nodes)+len(model.edges)+len(model.views),
                "type": 'metric'
            },
        }
    # END of calculate

    def get_name(self):
        return 'CycleDetectionMetric'
    # END get_name
# END CycleDetectionMetric
