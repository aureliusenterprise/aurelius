from math import log

import networkx
import numpy as np
from pandas import DataFrame

from m4i_analytics.graphs.GraphUtils import GraphUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    Aspect,
    ElementType,
    Layer,
    RelationshipType,
)
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute


class GraphComplexity:
    @staticmethod
    def number_of_nodes(graph):
        """
        Counts the number of nodes in your graph.

        :returns: The number of nodes in your graph.
        :rtype: int

        :param Graph graph: The graph for which to count the nodes.
        """

        return len(graph.nodes)

    # END number_of_nodes

    @staticmethod
    def number_of_edges(graph):
        """
        Counts the number of edges in your graph.

        :returns: The number of edges in your graph.
        :rtype: int

        :param Graph graph: The graph for which to count the edges.
        """

        return len(graph.edges)

    # END number_of_edges

    @staticmethod
    def number_of_node_types(graph):
        """
        Counts the number of unique node types in your graph.

        :returns: The number of unique node types in your graph.
        :rtype: int

        :param Graph graph: The graph for which to count the unique node types.
        """

        return len(graph.nodes.groupby(by=graph.getNodeAttributeMapping(NodeAttribute.TYPE)))

    # END number_of_node_types

    @staticmethod
    def number_of_edge_types(graph):
        """
        Counts the number of unique edge types in your graph.

        :returns: The number of unique edge types in your graph.
        :rtype: int

        :param Graph graph: The graph for which to count the unique edge types.
        """

        return len(graph.edges.groupby(by=graph.getEdgeAttributeMapping(EdgeAttribute.TYPE)))

    # END number_of_edge_types

    @staticmethod
    def in_degree(graph, return_node=False):
        """
        Calculates the in-degree for all nodes in your graph.

        :returns: A DataFrame containing the in-degree for all nodes in the
            graph along the dimensions node x count
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the in-degrees
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        transition_matrix = GraphUtils.toTransitionMatrix(graph)
        result = transition_matrix.groupby(by="target").size().reset_index()
        assert result is not None  # groupby().size().reset_index() should not return None
        result.columns = ["node", "count"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END in_degree

    @staticmethod
    def out_degree(graph, return_node=False):
        """
        Calculates the out-degree for all nodes in your graph.

        :returns: A DataFrame containing the out-degree for all nodes in the
            graph along the dimensions node x count
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the out-degrees
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        transition_matrix = GraphUtils.toTransitionMatrix(graph)
        result = transition_matrix.groupby(by="source").size().reset_index()
        assert result is not None  # groupby().size().reset_index() should not return None
        result.columns = ["node", "count"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END out_degree

    @staticmethod
    def model_heterogeneity(graph):
        """
        Calculate the similarity of the nodes and edges in a model relative to
        one another (heterogeneity). Entropy is used as a measure of
        heterogeneity.

        :returns: The heterogeneity of the model
        :rtype: double

        :param Graph graph: The graph for which to calculate its heterogeneity
        """
        pass

    # END model_heterogeneity

    @staticmethod
    def degree_centrality(graph, return_node=False):
        """
        Calculates for every node in the graph the fraction of nodes it is
        connected to

        :returns: A DataFrame containing the degree centrality for all nodes in
            the graph along the dimensions node x degree
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the degree centrality
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        degree_centrality = networkx.degree_centrality(nx)
        result = DataFrame.from_dict(degree_centrality, orient="index").reset_index()
        result.columns = ["node", "degree"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END degree_centrality

    @staticmethod
    def in_degree_centrality(graph, return_node=False):
        """
        Calculates for every node in the graph the fraction of nodes its incoming
        edges are connected to

        :returns: A DataFrame containing the in-degree centrality for all nodes
            in the graph along the dimensions node x degree
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the in-degree centrality
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        in_degree_centrality = networkx.in_degree_centrality(nx)
        result = DataFrame.from_dict(in_degree_centrality, orient="index").reset_index()
        result.columns = ["node", "degree"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END in_degree_centrality

    @staticmethod
    def out_degree_centrality(graph, return_node=False):
        """
        Calculates for every node in the graph the fraction of nodes its outgoing
        edges are connected to

        :returns: A DataFrame containing the out-degree centrality for all nodes
            in the graph along the dimensions node x degree
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the out-degree centrality
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        out_degree_centrality = networkx.out_degree_centrality(nx)
        result = DataFrame.from_dict(out_degree_centrality, orient="index").reset_index()
        result.columns = ["node", "degree"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END out_degree_centrality

    @staticmethod
    def closeness_centrality(graph, return_node=False):
        """
        Calculates for every node in the graph the sum of the shortest path
        distances to all other nodes. By default, the result is normalized by
        the amount of other nodes in the graph.

        :returns: A DataFrame containing the closeness centrality for all nodes
            in the graph along the dimensions node x value.
        :rtype: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the closeness centrality
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        closeness_centrality = networkx.closeness_centrality(nx)
        result = DataFrame.from_dict(closeness_centrality, orient="index").reset_index()
        result.columns = ["node", "value"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END closeness_centrality

    @staticmethod
    def betweenness_centrality(graph, return_node=False):
        """
        Calculates for every node in the graph the sum of the fraction of
        all-pairs shortest paths that pass through that node.

        :returns: A DataFrame containing the betweenness centrality for all
            nodes in the graph along the dimensions node x value.
        :rtye: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the betweenness centrality
        :param bool return_node: *Optional*. If true, returns the complete node
            in the node column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        betweenness_centrality = networkx.betweenness_centrality(nx)
        result = DataFrame.from_dict(betweenness_centrality, orient="index").reset_index()
        result.columns = ["node", "value"]  # type: ignore[reportAttributeAccessIssue]

        if return_node:
            result.node = result.node.map(lambda n: graph.getNodeById(n))

        return result

    # END betweenness_centrality

    @staticmethod
    def edge_betweenness_centrality(graph, return_edge=False):
        """
        Calculates for every edge in the graph the sum of the fraction of
        all-pairs shorteste paths that pass through that edge.

        :returns: A DataFrame containing the betweenness centrality for all
            edges in the graph along the dimensions edge x value.
        :rtye: pandas.DataFrame

        :param Graph graph: The graph for which to calculate the edge betweenness centrality
        :param bool return_edge: *Optional*. If true, returns the complete edge
            in the edge column. If false, only returns the ID. By default, is false.
        """

        nx = GraphUtils.toNXGraph(graph)
        out_degree_centrality = networkx.edge_betweenness_centrality(nx)
        result = DataFrame.from_dict(out_degree_centrality, orient="index").reset_index()
        result.columns = ["edge", "value"]  # type: ignore[reportAttributeAccessIssue]
        result.edge = result.edge.map(lambda e: graph.getEdgeByEndpoints(e[0], e[1]))

        if return_edge:
            result.edge = result.edge.map(lambda e: graph.getEdgeById(e))

        return result

    # END edge_betweenness_centrality

    @staticmethod
    def _assess_way_of_working(nodes_entropy, edges_entropy):
        result = "hard to make an assessment"
        if edges_entropy <= 0.125:
            if nodes_entropy <= 0.1:
                result = "Good basic model to work forward"
            else:
                result = (
                    "Model is unbalanced. Possible reasons: Some relationships"
                    " missing or overuse of relationship types"
                )
        else:
            if nodes_entropy <= 0.1:
                result = "Model is unbalanced. Possible reasons: Modeling patterns are not applied"
            else:
                result = "Good model with a balanced use of concept and relation types"
        return result

    # END assess_way_of_working

    @staticmethod
    def way_of_working_dynamics(h1, h2, h1_old, h2_old):
        direction = "no clear direction observed"
        qualifier = ""

        if h1 is not None and h2 is not None and h1_old is not None and h2_old is not None:
            d_h1 = h1 - h1_old
            d_h2 = h2 - h2_old

            distance = pow((pow(d_h1, 2) + pow(d_h2, 2)), 0.5)

            if distance > 0.01:
                qualifier = "high dynamics" if distance > 0.1 else "regular dynamics"

                if d_h1 > 0 and d_h2 > 0:
                    direction = "extend model accross multiple layers"

                if d_h1 > 0 and d_h2 < 0:
                    direction = "risk of model patterns are not applied"

                if d_h1 < 0 and d_h2 > 0:
                    direction = "harmonization of model"

                if d_h1 < 0 and d_h2 < 0:
                    direction = "reduction of model"

        return "{}{}{}".format(qualifier, ": " * bool(qualifier), direction).capitalize()

    # END way_of_working_dynamics

    @staticmethod
    def way_of_working(model):
        """
        Assesses the current state of the model based on the use of different
        types of nodes and relationships.

        The measure used is heterogeneity, which is based on entropy:

        The higher the entropy the more heterogeneous the usage of relations is
            -> more different relations are used could be because of a bad model or
               extending the model to cover more of the context

        The lower the entropy the less different relation types are used
            -> less different relation types means that the model is using fewer relation types
               means a bad model or focus on a particular layer of the model

        This metric is independent of the number of concepts in the model
        """

        def entropy(p):
            return -p * log(p)

        # END entropy

        grouped_model = GraphUtils.groupByNodeType(model)
        edges = grouped_model.edges

        edge_source_key = grouped_model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)

        n = len(ElementType.getAll()) * len(ElementType.getAll()) * len(RelationshipType.getAll())

        edges_entropy = 0
        for _index, row in edges.iterrows():
            s = row[edge_source_key]
            su = edges[edges[edge_source_key] == s].agg({"count": np.sum})  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
            p = row["count"] / su / n * len(ElementType.getAll())
            edges_entropy += entropy(p)
        # END LOOP
        edges_entropy = edges_entropy["count"]  # type: ignore[reportGeneralTypeIssues]

        node_types = DataFrame.from_records(model.nodes.type.dropna())
        node_types.columns = ["typename", "tag", "layer", "aspect"]  # type: ignore[reportAttributeAccessIssue]
        nodes = (
            node_types.groupby(by=["aspect", "layer"]).size()
            / len(node_types)
            / (len(Aspect.getAll()) * len(Layer.getAll()))
        )

        nodes_entropy = nodes.apply(lambda p: entropy(p)).sum()

        assessment = GraphComplexity._assess_way_of_working(nodes_entropy, edges_entropy)

        return {"h1": edges_entropy, "h2": nodes_entropy, "assessment": assessment}

    # END way_of_working


# END GraphComplexity
