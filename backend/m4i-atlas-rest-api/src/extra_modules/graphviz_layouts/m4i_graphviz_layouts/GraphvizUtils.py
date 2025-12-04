from m4i_analytics.graphs.model.Graph import NodeAttribute, EdgeAttribute

from graphviz import Digraph


class GraphvizUtils(object):

    @staticmethod
    def to_graphviz_graph(graph, node_attrs={}):

        """
        Generates a Graphviz instance based on the given graph that can be used for analysis and visualization purposes.
        :returns: A new Grahphviz instance of the given graph, along with a mapping of the original graph's node ids to the ids used for the graphviz nodes
        :rtype: generator of graphviz.DiGraph, dict

        :param Graph graph: The graph you wish to convert
        :param dict node_attrs: Attributes you wish to assign to the nodes, keyed by node ID
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                'One or more graph attributes are not mapped correctly! Please ensure the attribute mapping is correct before doing any analyses.')

        node_name_key = graph.getNodeAttributeMapping(NodeAttribute.ID)

        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)
        edge_label_key = graph.getEdgeAttributeMapping(EdgeAttribute.LABEL)


        # By hashing the ID's , we get rid of any potential special characters graphviz does not like
        # A graphviz ID always needs to start with a character
        node_names = {node[node_name_key]: 'id_{}'.format(abs(hash(node[node_name_key]))) for node in graph.nodes.to_dict(orient='records')}

        mapped_node_attrs = {node_names['key']: value for key, value in node_attrs.items()}

        gvz = Digraph(node_attr=mapped_node_attrs)

        for node in graph.nodes.to_dict(orient='records'):
            gvz.node(node_names[node[node_name_key]]
                , 'label for width')
        # END LOOP

        for edge in graph.edges.to_dict(orient='records'):
            gvz.edge(node_names[edge[edge_source_key]]
                , node_names[edge[edge_target_key]]
                , edge.get(edge_label_key, ''))
        # END LOOP

        yield gvz

        # Unless the caller needs the mapping, this code is never executed
        node_name_mapping = {value: key for key, value in node_names.items()}

        yield node_name_mapping
    # END to_graphviz_graph
# END GraphvizUtils