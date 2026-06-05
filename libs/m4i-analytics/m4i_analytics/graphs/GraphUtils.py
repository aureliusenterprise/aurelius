from graphviz import Digraph
from networkx import DiGraph as nxDiGraph
from pandas import DataFrame, isna

from m4i_analytics.graphs.model.Graph import EdgeAttribute, Graph, NodeAttribute


class GraphUtils:
    @staticmethod
    def isValid(graph):
        """
        Determines whether the given graph is valid by checking whether every
        edge in the graph has a node as its source and target

        :returns: Whether or not the given graph is valid
        :rtype: bool

        :param Graph graph: The graph you wish to determine the validity of
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        node_id_key = graph.getNodeAttributeMapping(NodeAttribute.ID)
        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        node_ids = graph[node_id_key].toList()
        return not filter(
            lambda e: e.get(edge_source_key) not in node_ids or e.get(edge_target_key) not in node_ids,
            graph.edges.to_dict(orient="records"),
        )

    # END isValid

    @staticmethod
    def groupByNodeType(graph):
        """
        Generates a new graph based on the given graph in which all nodes have been aggregated based on type.

        :returns: A new graph in which all nodes have been aggregated based on type.
        :rtype: Graph

        :param Graph graph: The graph you wish to aggregate
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        node_id_key = graph.getNodeAttributeMapping(NodeAttribute.ID)
        node_type_key = graph.getNodeAttributeMapping(NodeAttribute.TYPE)
        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        nodes_df = graph.nodes
        edges_df = graph.edges

        grouped_nodes_cols = ["type", "count"]
        grouped_nodes = nodes_df.groupby(by=node_type_key).size().reset_index()
        grouped_nodes.columns = grouped_nodes_cols

        joined_edges_cols = ["type", "source", "target"]
        joined_edges = edges_df.merge(
            nodes_df, left_on=edge_source_key, right_on=node_id_key, how="left"
        ).merge(nodes_df, left_on=edge_target_key, right_on=node_id_key, how="left")[
            ["type_x", "type_y", "type"]
        ]
        joined_edges.columns = joined_edges_cols

        grouped_edges_cols = ["type", "source", "target", "count"]
        grouped_edges = joined_edges.groupby(by=joined_edges_cols).size().reset_index()
        grouped_edges.columns = grouped_edges_cols
        grouped_edges["id"] = grouped_edges.index + 1

        grouped_graph = Graph(**{"id": graph.id, "nodes": grouped_nodes, "edges": grouped_edges})

        grouped_graph.putNodeAttributeMapping(NodeAttribute.ID, "type")
        grouped_graph.putNodeAttributeMapping(NodeAttribute.TYPE, "type")
        grouped_graph.putNodeAttributeMapping(NodeAttribute.NAME, "type")
        grouped_graph.putNodeAttributeMapping(NodeAttribute.LABEL, "type")
        grouped_graph.putNodeAttributeMapping("count", "count")

        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.ID, "id")
        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.TYPE, "type")
        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.SOURCE, "source")
        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.TARGET, "target")
        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.NAME, "type")
        grouped_graph.putEdgeAttributeMapping(EdgeAttribute.LABEL, "type")
        grouped_graph.putEdgeAttributeMapping("count", "count")

        return grouped_graph

    # END groupByNodeType

    @staticmethod
    def toBipartiteGraph(graph):
        """
        Generates a new graph based on the given graph in which all edges have been modeled as nodes.

        :returns: A new graph in which all edges have been modeled as nodes
        :rtype: Graph

        :param Graph graph: The graph you wish to aggregate
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        node_id_key = graph.getNodeAttributeMapping(NodeAttribute.ID)
        node_type_key = graph.getNodeAttributeMapping(NodeAttribute.TYPE)
        node_name_key = graph.getNodeAttributeMapping(NodeAttribute.NAME)
        node_label_key = graph.getNodeAttributeMapping(NodeAttribute.LABEL)

        edge_id_key = graph.getEdgeAttributeMapping(EdgeAttribute.ID)
        edge_type_key = graph.getEdgeAttributeMapping(EdgeAttribute.TYPE)
        edge_name_key = graph.getEdgeAttributeMapping(EdgeAttribute.NAME)
        edge_label_key = graph.getEdgeAttributeMapping(EdgeAttribute.LABEL)
        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        # Map every edge in the graph to a new node
        nodes = graph.nodes.to_dict(orient="records") + list(
            map(
                lambda e: {
                    node_id_key: e.get(edge_id_key),
                    node_type_key: e.get(edge_type_key),
                    node_name_key: e.get(edge_name_key),
                    node_label_key: e.get(edge_label_key),
                },
                graph.edges.to_dict(orient="records"),
            )
        )

        # Create two new edges for every edge we mapped to a node (one from
        # the original source node to the new edge node, and one from the new
        # edge node to the original target node).
        bipartite_edge_sets = map(
            lambda e: [
                {
                    "id": e.get(edge_id_key) + "-src",
                    "name": "source",
                    "label": "source",
                    "source": e.get(edge_source_key),
                    "target": e.get(edge_id_key),
                    "type": "bipartite_edge",
                },
                {
                    "id": e.get(edge_id_key) + "-trg",
                    "name": "target",
                    "label": "target",
                    "source": e.get(edge_id_key),
                    "target": e.get(edge_target_key),
                    "type": "bipartite_edge",
                },
            ],
            graph.edges.to_dict(orient="records"),
        )

        # Do a flat map on the edge sets to arrive at a single list of edges
        edges = [edge for set in bipartite_edge_sets for edge in set]

        bipartite_graph = Graph(**{"id": graph.id, "nodes": DataFrame(nodes), "edges": DataFrame(edges)})

        bipartite_graph.putNodeAttributeMapping(NodeAttribute.ID, node_id_key)
        bipartite_graph.putNodeAttributeMapping(NodeAttribute.TYPE, node_type_key)
        bipartite_graph.putNodeAttributeMapping(NodeAttribute.NAME, node_name_key)
        bipartite_graph.putNodeAttributeMapping(NodeAttribute.LABEL, node_label_key)

        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.ID, "id")
        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.TYPE, "type")
        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.SOURCE, "source")
        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.TARGET, "target")
        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.NAME, "name")
        bipartite_graph.putEdgeAttributeMapping(EdgeAttribute.LABEL, "label")

        return bipartite_graph

    # END toBipartiteGraph

    @staticmethod
    def toNXGraph(graph):
        """
        Generates a networkX instance based on the given graph that can be used
        for analysis and visualization purposes.

        :returns: A new networkX instance of the given graph
        :rtype: networkx.DiGraph

        :param Graph graph: The graph you wish to convert
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        node_id_key = graph.getNodeAttributeMapping(NodeAttribute.ID)
        node_name_key = graph.getNodeAttributeMapping(NodeAttribute.NAME)
        node_type_key = graph.getNodeAttributeMapping(NodeAttribute.TYPE)
        node_label_key = graph.getNodeAttributeMapping(NodeAttribute.LABEL)

        edge_id_key = graph.getEdgeAttributeMapping(EdgeAttribute.ID)
        edge_name_key = graph.getEdgeAttributeMapping(EdgeAttribute.NAME)
        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)
        edge_type_key = graph.getEdgeAttributeMapping(EdgeAttribute.TYPE)
        edge_label_key = graph.getEdgeAttributeMapping(EdgeAttribute.LABEL)

        result = nxDiGraph()
        nodes = []
        node_ids = []
        for node in graph.nodes.to_dict(orient="records"):
            node_type = node.get(node_type_key, {})
            # Replace NaN type with an empty dictionary
            node_type = node_type if not isna(node_type) else {}

            nodes.append(
                (
                    node.get(node_id_key),
                    {
                        node_id_key: node[node_id_key],
                        node_name_key: node[node_name_key],
                        node_label_key: node[node_label_key],
                        "type_name": node_type.get("typename", None),
                        "type_tag": node_type.get("tag", None),
                        "type_aspect": node_type.get("aspect", None),
                        "type_layer": node_type.get("layer", None),
                    },
                )
            )
            node_ids.append(node[node_id_key])
        # END LOOP
        result.add_nodes_from(nodes)

        edges = []
        for edge in graph.edges.to_dict(orient="records"):
            if edge.get(edge_source_key) in node_ids and edge.get(edge_target_key) in node_ids:
                edge_type = edge.get(edge_type_key, {})
                # Replace NaN type with an empty dictionary

                edge_type = edge_type if not isna(edge_type) else {}
                # disregard all relations to relations
                edge_attr = {
                    edge_id_key: edge[edge_id_key],
                    edge_name_key: edge[edge_name_key],
                    edge_label_key: edge[edge_label_key],
                    "type_name": edge_type.get("typename", None),
                    "type_tag": edge_type.get("tag", None),
                    "type_aspect": edge_type.get("relcls", None),
                    "type_shorthand": edge_type.get("shorthand", None),
                    "weight": edge_type.get("weight", 1),
                }
                edges.append((edge.get(edge_source_key), edge.get(edge_target_key), edge_attr))
        # END LOOP
        result.add_edges_from(edges)

        return result
        # END toNXGraph

    @staticmethod
    def toTransitionMatrix(graph):
        """
        Generates a transition matrix for the given graph along three dimensions: source x target x type

        :returns: A pandas DataFrame containing the transition matrix
        :rtype: DataFrame

        :param Graph graph: The graph for which you wish to calculate the transition matrix
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)
        edge_type_key = graph.getEdgeAttributeMapping(EdgeAttribute.TYPE)

        transitions = list(
            map(
                lambda e: {
                    "source": e.get(edge_source_key),
                    "target": e.get(edge_target_key),
                    "type": e.get(edge_type_key),
                },
                graph.edges.to_dict(orient="records"),
            )
        )

        return DataFrame(transitions)

    # END toTransitionMatrix

    @staticmethod
    def toGraphvizGraph(graph, node_attrs=None):
        """
        Generates a Graphviz instance based on the given graph that can be used
        for analysis and visualization purposes.
        :returns: A new Grahphviz instance of the given graph, along with a
            mapping of the original graph's node ids to the ids used for the
            graphviz nodes
        :rtype: generator of graphviz.DiGraph, dict

        :param Graph graph: The graph you wish to convert
        :param dict node_attrs: Attributes you wish to assign to the nodes, keyed by node ID
        """

        if node_attrs is None:
            node_attrs = {}
        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly!"
                " Please ensure the attribute mapping is correct before"
                " doing any analyses."
            )

        node_name_key = graph.getNodeAttributeMapping(NodeAttribute.ID)

        edge_source_key = graph.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        edge_target_key = graph.getEdgeAttributeMapping(EdgeAttribute.TARGET)
        edge_label_key = graph.getEdgeAttributeMapping(EdgeAttribute.LABEL)

        # By hashing the ID's , we get rid of any potential special characters graphviz does not like
        # A graphviz ID always needs to start with a character
        node_names = {
            node[node_name_key]: f"id_{abs(hash(node[node_name_key]))}"
            for node in graph.nodes.to_dict(orient="records")
        }

        mapped_node_attrs = {node_names[key]: value for key, value in node_attrs.items()}

        gvz = Digraph(node_attr=mapped_node_attrs)

        for node in graph.nodes.to_dict(orient="records"):
            gvz.node(node_names[node[node_name_key]], "label for width")
        # END LOOP

        for edge in graph.edges.to_dict(orient="records"):
            gvz.edge(
                node_names[edge[edge_source_key]],
                node_names[edge[edge_target_key]],
                edge.get(edge_label_key, ""),
            )
        # END LOOP

        yield gvz

        # Unless the caller needs the mapping, this code is never executed
        node_name_mapping = {value: key for key, value in node_names.items()}

        yield node_name_mapping

    # END toGraphvizGraph

    @staticmethod
    def loadGraphData(graph, data):
        """
        Loads data retrieved from the repository into the given graph.

        :returns: The given graph with data loaded into it
        :rtype: Graph

        :param Graph graph: The graph that is the target of the data
        :param DataRetrieve data: The data that should be loaded into the graph
        """

        data_to_load = [{"id": content.id, "data": content.data} for content in data.content if data.content]

        graph.data = DataFrame(data_to_load)

        return graph

    # END loadGraphData


# END GraphUtils
