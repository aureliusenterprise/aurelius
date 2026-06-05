from enum import Enum
from typing import cast

import matplotlib.pyplot as plt
import networkx as nx
import pydotplus as ptp
import pydotplus.graphviz
from graphviz import Digraph

from m4i_analytics.graphs.GraphUtils import GraphUtils
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute


class Layout(Enum):
    CIRCULAR = 0
    FRUCHTERMAN_REINGOLD = 1
    KAMADA_KAWAI = 2
    RANDOM = 3
    SHELL = 4
    SPECTRAL = 5
    HIERARCHICAL = 6
    MANUAL = 7


# END Layout


class GraphPlotter:
    @staticmethod
    def _calculate_hierarchical_coordinates(graph, dpi=80, node_width=0.1, node_height=0.1):
        result = GraphUtils.toGraphvizGraph(graph)
        gvz = cast(Digraph, next(result))
        node_name_mapping = next(result)

        gvz.attr(dpi=str(dpi), rankdir="BT", nodesep="1", ranksep="2")
        gvz.attr("node", width=str(node_width), height=str(node_height))

        dot = gvz.pipe("dot")
        parsed_dot: pydotplus.graphviz.Dot = ptp.parser.parse_dot_data(dot)  # type: ignore[assignment]

        return {
            node_name_mapping[node.obj_dict["name"].strip('"')]: node.obj_dict["attributes"]["pos"][
                1:-1
            ].split(",")
            for node in parsed_dot.get_node_list()
            if "pos" in node.obj_dict["attributes"]
        }

    # END _calculate_hierarchical_coordinates

    @staticmethod
    def _get_coordinates(
        graph,
        layout,
        center_x,
        center_y,
        node_distance,
        scale,
        shell_list,
        weight_attr,
        coords,
        node_width,
        node_height,
    ):
        result = None

        if isinstance(layout, Layout):
            layout = layout.value

        if Layout.CIRCULAR.value == layout:
            result = nx.circular_layout(GraphUtils.toNXGraph(graph), center=[center_x, center_y], scale=scale)

        elif Layout.FRUCHTERMAN_REINGOLD.value == layout:
            result = nx.fruchterman_reingold_layout(
                GraphUtils.toNXGraph(graph),
                center=[center_x, center_y],
                scale=scale,
                k=node_distance,
            )

        elif Layout.KAMADA_KAWAI.value == layout:
            result = nx.kamada_kawai_layout(
                GraphUtils.toNXGraph(graph),
                center=[center_x, center_y],
                weight=weight_attr,
                dist=node_distance,
                scale=scale,
            )

        elif Layout.RANDOM.value == layout:
            result = nx.random_layout(GraphUtils.toNXGraph(graph), center=[center_x, center_y])

        elif Layout.SHELL.value == layout:
            result = nx.shell_layout(
                GraphUtils.toNXGraph(graph),
                center=[center_x, center_y],
                nlist=shell_list,
                scale=scale,
            )

        elif Layout.SPECTRAL.value == layout:
            result = nx.spectral_layout(
                GraphUtils.toNXGraph(graph),
                center=[center_x, center_y],
                weight=weight_attr,
                scale=scale,
            )

        elif Layout.HIERARCHICAL.value == layout:
            result = GraphPlotter._calculate_hierarchical_coordinates(
                graph, node_width=node_width, node_height=node_height
            )

        elif Layout.MANUAL.value == layout:
            result = coords

        return result

    # END _get_coordinates

    @staticmethod
    def get_coordinates(
        graph,
        layout=Layout.RANDOM,
        center_x=0,
        center_y=0,
        node_distance=None,
        scale=1,
        shell_list=None,
        weight_attr=None,
        coords=None,
        node_width=0.1,
        node_height=0.1,
    ):
        """
        Calculate the coordinates of the nodes of your graph based on
        the given layout type.

        :returns: A dictionary of positions keyed by node id.
        :rtype: dict

        :param Graph graph: The graph you want to display.
        :param bool arrows: *Optional*. Whether your edges should have arrow
            heads (source -> target). Defaults to False.
        :param int center_x: *Optional*. The center of your graph along the x
            axis. Use this to offset your graph horizontally. Defaults to 0.
        :param int center_y: *Optional*. The center of your graph along the y
            axis. Use this to offset your graph vertically. Defaults to 0.
        :param double edge_alpha: *Optional*. Specify the opacity of your edges
            on a scale between 0 to 1. Defaults to 1.
        :param int edge_width: *Optional*. The width of the edges in the graph.
            Defaults to 1.
        :param str font_family: *Optional*. The font family in which to render
            the labels of the graph. Defaults to 'sans_serif'.
        :param int font_size: *Optional*. The font size in which to render the
            labels of the graph. Defaults to 8.
        :param Layout layout: *Optional*. The layout algorithm to use for
            rendering the graph. Defaults to Layout.RANDOM.
        :param double nodes_alpha: *Optional*. Specify the opacity of your nodes
            on a scale between 0 to 1. Defaults to 1.
        :param str node_color: *Optional*. The color in which to render the
            nodes. Defaults to "black".
        :param any node_distance: *Optional*. Some layout algorithms allow you
            to specify the optimal distance between nodes. For the Fruchterman
            Reingold layout, this parameter should be an integer. For the Kamada
            Kawai layout, this parameter should be a two-level dict of optimal
            distances, indexed by source and destination nodes. Defaults to None.
        :param str node_shape: *Optional*. The shape in which to render the
            nodes. Defaults to "o".
        :param int node_size: *Optional*. The size in which to render the nodes.
            Defaults to 250.
        :param int scale: *Optional*. The scale at which to render the graph.
            Defaults to 100.
        :param array shell_list: *Optional*. A two-dimensional array of node id's
            specifying which node should be rendered at which level of the graph.
            Defaults to None.
        :param str weight_attr: *Optional*. The name of the attribute that defines
            the weight of the edges in your graph. This is used with the Kamada
            Kawai and Spectral layouts. Defaults to None.
        :param dict coords: *Optional*. The coordinates per node that should be
            returned for the manual layout. Defaults to {}.
        """
        if coords is None:
            coords = {}
        return GraphPlotter._get_coordinates(
            graph,
            layout,
            center_x,
            center_y,
            node_distance,
            scale,
            shell_list,
            weight_attr,
            coords,
            node_width,
            node_height,
        )

    # END get_coordinates

    @staticmethod
    def visualize(
        graph,
        arrows=False,
        center_x=0,
        center_y=0,
        edge_alpha=1,
        edge_width=1,
        font_family="sans_serif",
        font_size=8,
        layout=Layout.RANDOM,
        node_alpha=1,
        node_color="black",
        node_distance=None,
        node_shape="o",
        node_size=100,
        scale=100,
        shell_list=None,
        weight_attr=None,
    ):
        """
        Render a visualization of your graph. This function opens a matplot
        dialog that renders the visualization. You can optionally specify the
        layout algorithm, as well as other parameters to customize the way your
        graph looks.

        :param Graph graph: The graph you want to display.
        :param bool arrows: *Optional*. Whether your edges should have arrow
            heads (source -> target). Defaults to False.
        :param int center_x: *Optional*. The center of your graph along the x
            axis. Use this to offset your graph horizontally. Defaults to 0.
        :param int center_y: *Optional*. The center of your graph along the y
            axis. Use this to offset your graph vertically. Defaults to 0.
        :param double edge_alpha: *Optional*. Specify the opacity of your edges
            on a scale between 0 to 1. Defaults to 1.
        :param int edge_width: *Optional*. The width of the edges in the graph.
            Defaults to 1.
        :param str font_family: *Optional*. The font family in which to render
            the labels of the graph. Defaults to 'sans_serif'.
        :param int font_size: *Optional*. The font size in which to render the
            labels of the graph. Defaults to 8.
        :param Layout layout: *Optional*. The layout algorithm to use for
            rendering the graph. Defaults to Layout.RANDOM.
        :param double nodes_alpha: *Optional*. Specify the opacity of your nodes
            on a scale between 0 to 1. Defaults to 1.
        :param str node_color: *Optional*. The color in which to render the
            nodes. Defaults to "black".
        :param any node_distance: *Optional*. Some layout algorithms allow you
            to specify the optimal distance between nodes. For the Fruchterman
            Reingold layout, this parameter should be an integer. For the Kamada
            Kawai layout, this parameter should be a two-level dict of optimal
            distances, indexed by source and destination nodes. Defaults to None.
        :param str node_shape: *Optional*. The shape in which to render the
            nodes. Defaults to "o".
        :param int node_size: *Optional*. The size in which to render the nodes.
            Defaults to 250.
        :param int scale: *Optional*. The scale at which to render the graph.
            Defaults to 100.
        :param array shell_list: *Optional*. A two-dimensional array of node id's
            specifying which node should be rendered at which level of the graph.
            Defaults to None.
        :param str weight_attr: *Optional*. The name of the attribute that
            defines the weight of the edges in your graph. This is used with the
            Kamada Kawai and Spectral layouts. Defaults to None.
        """

        if not graph.hasValidAttributeMapping():
            raise ValueError(
                "One or more graph attributes are not mapped correctly! "
                "Please ensure the attribute mapping is correct before "
                "doing any visualizations."
            )

        node_id_key = graph.getNodeAttributeMapping(NodeAttribute.ID)
        node_label_key = graph.getNodeAttributeMapping(NodeAttribute.LABEL)

        edge_label_key = graph.getEdgeAttributeMapping(EdgeAttribute.LABEL)

        nxgraph = GraphUtils.toNXGraph(graph)

        plt.figure()
        plt.plot()

        coords = GraphPlotter._get_coordinates(
            nxgraph,
            layout,
            center_x,
            center_y,
            node_distance,
            scale,
            shell_list,
            weight_attr,
            coords=None,
            node_width=1,
            node_height=1,
        )

        if coords is None:
            raise ValueError("Invalid layout specified, cannot compute coordinates.")

        nx.draw_networkx_nodes(
            nxgraph,
            coords,
            node_shape=node_shape,
            node_color=node_color,
            node_size=node_size,
            alpha=node_alpha,
        )
        nx.draw_networkx_edges(
            nxgraph,
            coords,
            arrows=arrows,
            width=edge_width,
            alpha=edge_alpha,  # type: ignore[arg-type]
        )

        node_labels = {
            n.get(node_id_key): n.get(node_label_key) for n in graph.nodes.to_dict(orient="records")
        }

        edge_labels = dict(
            [
                (
                    (
                        u,
                        v,
                    ),
                    d["attr_dict"][edge_label_key],
                )
                for (u, v, d) in nxgraph.edges(data=True)
            ]
        )

        nx.draw_networkx_labels(nxgraph, coords, node_labels, font_size=font_size, font_family=font_family)
        nx.draw_networkx_edge_labels(
            nxgraph, coords, edge_labels, font_size=font_size, font_family=font_family
        )

        plt.show()

    # END visualize


# END GraphPlotter
