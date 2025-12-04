import copy

import networkx as nx
import pandas as pd
from m4i_analytics.graphs.GraphUtils import GraphUtils
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import \
    ArchimateModel
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

unconnected_elems_config = MetricConfig(**{
    'description': 'These elements are not connected to any other elements',
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
        'type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'

        })
    }
})

clusters_config = MetricConfig(**{
    'description': 'Each row represents a cluster in the model',
    'color_column': 'group',
    'id_column': 'id',
    'data': {
        'group': MetricColumnConfig(**{
            'displayName': 'Group',
            'description': 'The id of the cluster'
        }),
        'id': MetricColumnConfig(**{
            'displayName': 'Concept id',
            'description': 'The id of the concept'

        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'

        })
    }
})

UNCONNECTED_CLUSTER_ID = 'Unconnected'


def cluster_nodes(clusters):
    """
    Flatten the given clusters into a sequence of tuples of node IDs and cluster IDs.
    Nodes with no incoming or outgoing relationships are grouped into a single cluster.
    """
    # Start with ID 1
    for index, cluster in enumerate(clusters, 1):

        # Group all elements that do not have any incoming or outgoing relationships into
        # a single cluster
        cluster_id = index if len(cluster) > 1 else UNCONNECTED_CLUSTER_ID

        # Assign every node in the cluster its cluster ID and return the tuple
        for node in cluster:
            yield (cluster_id, node)
        # END LOOP
    # END LOOP
# END cluster_nodes


def get_partitions(model):
    """
    Finds unconnected clusters in the given model and returns the nodes per cluster as a pandas DataFrame
    """
    # Turn the given model into a graph and find the clusters
    graph = GraphUtils.toNXGraph(model)
    clusters = nx.connected_components(graph.to_undirected())

    # Get the nodes per cluster as a flat sequence
    clustered_nodes = cluster_nodes(clusters)

    # Return the nodes per cluster as a pandas DataFrame
    return pd.DataFrame(clustered_nodes, columns=['group', 'id'])
# END get_partitions


def edges_to_nodes(model: ArchimateModel):

    node_id_key = model.getNodeAttributeMapping(NodeAttribute.ID)

    edge_id_key = model.getEdgeAttributeMapping(EdgeAttribute.ID)
    source_key = model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
    target_key = model.getEdgeAttributeMapping(EdgeAttribute.TARGET)

    nodes = {}
    edges = {}

    # Replace the edges in the model by nodes
    for index, edge in model.edges.iterrows():

        # Get the attributes of the edge
        edge_id = edge[edge_id_key]
        source = edge[source_key]
        target = edge[target_key]

        # Create the node that replaces the edge
        node = {node_id_key: edge_id}

        # Create new incoming and outgoing edges
        incoming_edge_id = f'{edge_id}_in'
        incoming = {
            edge_id_key: incoming_edge_id,
            source_key: source,
            target_key: edge_id
        }

        outgoing_edge_id = f'{edge_id}_out'
        outgoing = {
            edge_id_key: outgoing_edge_id,
            source_key: edge_id,
            target_key: target
        }

        # Append the new node and edges to the result, indexed by ID
        nodes = {**nodes, edge_id: node}
        edges = {
            **edges,
            incoming_edge_id: incoming,
            outgoing_edge_id: outgoing
        }
    # END LOOP

    # Also include the already existing nodes
    for index, node in model.nodes.iterrows():
        node_id = node[node_id_key]
        nodes = {**nodes, node_id: {node_id_key: node_id}}
    # END LOOP

    # Return the model including the new nodes and edges. Keep other settings.
    model_with_edges_as_nodes = copy.copy(model)

    model_with_edges_as_nodes.nodes = pd.DataFrame(
        nodes.values(),
        columns=model.nodes.columns
    )
    model_with_edges_as_nodes.edges = pd.DataFrame(
        edges.values(),
        columns=model.edges.columns
    )

    return model_with_edges_as_nodes
# END edges_to_nodes


class UnconnectedElementsMetric(Metric):
    id = '0470d97a-d11e-47b1-970c-2ebdb1c35809'
    label = 'Unconnected Elements'
    unconnected_elems = None

    @staticmethod
    def calculate(model):

        model_with_edges_as_nodes = edges_to_nodes(model)

        partitions = get_partitions(model_with_edges_as_nodes)

        clusters = pd.DataFrame()
        unconnected_elems = pd.DataFrame()

        partition_count = partitions['group'].unique().size
        has_multiple_partitons = partition_count > 1

        if has_multiple_partitons:
            clusters = pd.merge(
                left=model.nodes,
                right=partitions,
                how='left',
                on='id'
            )

            # Return the type name rather than the complex type object
            clusters['type'] = clusters['type'].apply(lambda x: x['typename'])

            is_unconnected = clusters['group'] == UNCONNECTED_CLUSTER_ID
            unconnected_elems = clusters[is_unconnected]
        # END IF

        return {
            "unconnected elements": {
                "config": unconnected_elems_config,
                "data": unconnected_elems,
                "sample_size": len(model.nodes.index),
                "type": 'metric'
            },
            "clusters": {
                "config": clusters_config,
                "data": clusters,
                "sample_size": len(model.nodes.index),
                "type": 'metric'
            }
        }
    # END of calculate

    def get_name(self):
        return 'UnconnectedElementsMetric'
    # END get_name
# END UnconnectedElementsMetric
