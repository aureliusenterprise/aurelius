from collections import defaultdict
from typing import Iterable, Set

import pandas as pd
from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
    ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    RelationshipType, _RelationshipType)
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import \
    ArchimateModel

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

tree_property_config = MetricConfig(**{
    'description': 'Elements connected via aggregation, composition or specialization relations should form a tree structure i.e. have a single parent each. A child element violates the metric by having two or more parent elements',
    'id_column': 'id',
    'violation_column': 'is_violation',
    'color_column': 'tree',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'Child ID',
            'description': 'The identifier of the common child element'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the common child element'
        }),
        'type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the common child element'
        }),
        'rel_type': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The ArchiMate type of the relation between the child and parents'
        }),
        'cnt': MetricColumnConfig(**{
            'displayName': '# of Parents',
            'description': 'Total number of Parents of the common child element'
        })
    }
})


class BidirectionalMultiMap(defaultdict):

    inverse: defaultdict

    def __init__(self):
        super().__init__(set)
        self.inverse = defaultdict(set)
    # END __init__

    def add(self, key: str, *values: str):
        for value in values:
            self[key].add(value)
            self.inverse[value].add(key)
        # END LOOP
    # END add

# END BidirectionalMultiMap


def build_transition_matrix(edges: pd.DataFrame):
    matrix = BidirectionalMultiMap()
    for _, edge in edges.iterrows():
        edge_type = edge['type']
        if edge_type in [RelationshipType.COMPOSITION, RelationshipType.AGGREGATION]:
            matrix.add(edge['source'], edge['target'])
        else:
            matrix.add(edge['target'], edge['source'])
        # END IF
    # END LOOP
    return matrix
# END build_transition_matrix


def find_root_nodes(matrix: BidirectionalMultiMap):
    for node_id in matrix.keys():
        if node_id not in matrix.inverse:
            yield node_id
        # END IF
    # END LOOP
# END find_root_nodes


def find_nodes_in_tree(root_node: str, matrix: BidirectionalMultiMap, seen: Set[str] = None):

    # Track the nodes we have already seen to avoid getting stuck in a cycle.
    # Initialize the set if it is not given.
    if seen is None:
        seen = set()
    # END IF

    # If we have already seen this node, return.
    if root_node in seen:
        return
    # END IF

    # Return the current node and add it to the tracking set.
    yield root_node
    seen.add(root_node)

    # Check whether the key is present to avoid modifying the dictionary when using a defaultdict.
    if root_node in matrix:

        # Return all child nodes and their children.
        for child_node in matrix[root_node]:
            yield from find_nodes_in_tree(child_node, matrix, seen)
        # END LOOP
    # END IF
# END find_nodes_in_tree


def label_nodes_by_tree(transition_matrix: BidirectionalMultiMap):

    labeled_nodes = defaultdict(set)

    # Each root node represents a tree in the model.
    for root_node in find_root_nodes(transition_matrix):
        # Label every node in the tree by its root node. A node can have multiple lables.
        for node_id in find_nodes_in_tree(root_node, transition_matrix):
            labeled_nodes[node_id].add(root_node)
        # END LOOP
    # END LOOP

    return labeled_nodes
# END label_nodes_by_tree


def get_violating_nodes_for_relationship_type(model: ArchimateModel, relationship_type: _RelationshipType):
    # Filter relationships between elements on aggregation, composition and specialiation relations
    model_sliced = ArchimateUtils.sliceByEdgeType(model, [relationship_type])

    nodes = model_sliced.nodes
    sample_size = len(nodes)

    transition_matrix = build_transition_matrix(model_sliced.edges)
    labeled_nodes = label_nodes_by_tree(transition_matrix)

    nodes['cnt'] = nodes['id'].apply(lambda id: len(labeled_nodes[id]))

    violating_nodes = nodes[nodes['cnt'] > 1]

    violating_nodes['type'] = violating_nodes['type'].apply(
        lambda type: type['typename']
    )

    def get_node_name(node_id: str):
        nodes_matching_id = model.nodes[model.nodes['id'] == node_id]
        _, node = next(nodes_matching_id.iterrows())
        return node['name']
    # END get_node_name

    violating_nodes['tree'] = violating_nodes['id'].apply(
        lambda id: get_node_name(next(iter(labeled_nodes[id])))
    )

    violating_nodes['rel_type'] = relationship_type["typename"]

    violating_nodes['is_violation'] = violating_nodes['id'].apply(
        lambda id: (
            id in transition_matrix.inverse
            and len(transition_matrix.inverse[id]) > 1
        )
    )

    return sample_size, violating_nodes
# END get_violating_nodes_for_relationship_type


class TreeStructuresMetric(Metric):
    '''
    Determines violation of Tree Property for Elements connected via Aggregration/Composition/Specialization relationships
    '''
    id = '82cd0e9c-babe-46f4-8717-264d76115645'
    label = 'Tree Structures'

    @staticmethod
    def calculate(model):

        all_violating_nodes = pd.DataFrame()

        relationship_types = [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION
        ]

        total_sample_size = 0

        for relationship_type in relationship_types:
            sample_size, violating_nodes_for_relationship_type = get_violating_nodes_for_relationship_type(
                model,
                relationship_type
            )

            all_violating_nodes = pd.concat([
                all_violating_nodes,
                violating_nodes_for_relationship_type
            ])

            total_sample_size += sample_size
        # END LOOP
        # Filter relationships between elements on aggregation, composition and specialiation relations

        return {
            "tree structures": {
                "config": tree_property_config,
                "data": all_violating_nodes,
                "sample_size": total_sample_size,
                "type": 'metric',
            }
        }
    # END of calculate

    def get_name(self):
        return 'TreeStructuresMetric'
    # END get_name
# END TreeStructuresMetric
