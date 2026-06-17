from typing import Any

import pydotplus as ptp

from m4i_analytics.graphs.visualisations.model.Layout import Layout
from m4i_graphviz_layouts.GraphvizUtils import GraphvizUtils


class HierarchicalLayout(Layout):
    @staticmethod
    def get_coordinates(
        graph: Any,
        dpi: int = 80,
        rankdir: str = "BT",
        nodesep: float = 1,
        ranksep: float = 2,
        node_width: float = 0.1,
        node_height: float = 0.1,
        **kwargs: Any,
    ) -> dict:
        gen = GraphvizUtils.to_graphviz_graph(graph)
        gvz: Any = next(gen)
        _node_name_mapping: Any = next(gen, None)

        gvz.attr(dpi=str(dpi), rankdir=str(rankdir), nodesep=str(nodesep), ranksep=str(ranksep))

        gvz.attr("node", width=str(node_width), height=str(node_height))

        dot = gvz.pipe("dot")

        parsed_dot: Any = ptp.parser.parse_dot_data(dot)

        # If a list is returned, take the first graph
        parsed_graph: Any = parsed_dot if isinstance(parsed_dot, ptp.graphviz.Dot) else parsed_dot[0]

        result: dict = {}
        for node in parsed_graph.get_node_list():
            node_name = node.obj_dict["name"].strip('"')
            if "pos" in node.obj_dict["attributes"] and node_name in _node_name_mapping:
                result[_node_name_mapping[node_name]] = node.obj_dict["attributes"]["pos"][1:-1].split(",")
        return result

    # END get_coordinates

    @staticmethod
    def get_name() -> str:
        return "hierarchical"

    # END get_name


# END HierarchicalLayout
