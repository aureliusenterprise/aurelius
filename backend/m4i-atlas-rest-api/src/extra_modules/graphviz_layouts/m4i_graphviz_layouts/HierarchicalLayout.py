import pydotplus as ptp

from m4i_analytics.graphs.visualisations.model.Layout import Layout
from m4i_graphviz_layouts.GraphvizUtils import GraphvizUtils


class HierarchicalLayout(Layout):

    @staticmethod
    def get_coordinates(graph, dpi=80, rankdir='BT', nodesep=1, ranksep=2, node_width=0.1, node_height=0.1, **kwargs):

        gvz, node_name_mapping = GraphvizUtils.to_graphviz_graph(graph)

        gvz.attr(dpi=str(dpi), rankdir=str(rankdir),
                 nodesep=str(nodesep), ranksep=str(ranksep))

        gvz.attr('node', width=str(node_width), height=str(node_height))

        dot = gvz.pipe('dot')

        parsed_dot = ptp.parser.parse_dot_data(dot)

        # If a list is returned, take the first graph
        parsed_graph = parsed_dot if isinstance(
            parsed_dot, ptp.graphviz.Dot) else parsed_dot[0]

        return {node_name_mapping[node.obj_dict['name'].strip('"')]: node.obj_dict['attributes']['pos'][1:-1].split(',')
                for node in parsed_graph.get_node_list() if 'pos' in node.obj_dict['attributes'] and node.obj_dict['name'].strip('"') in node_name_mapping}
    # END get_coordinates

    @staticmethod
    def get_name():
        return 'hierarchical'
    # END get_name

# END HierarchicalLayout
