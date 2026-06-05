import copy
from array import array

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import RelationshipType
from m4i_analytics.graphs.model.Graph import EdgeAttribute
from m4i_analytics.graphs.visualisations.model.Layout import Layout


class ArchimateMatrixLayout(Layout):
    """
    Hierarchical layout algorithm for Archimate Models that arranges nodes in vertical levels
    based on the edges between them.
    """

    @staticmethod
    def _prepare_model(model):
        """
        Prepares a model for the hierarchical layout visualization by inverting
        all access writes and specialization relations.

        :param ArchimateModel model: The model that should be prepared.
        :return: A copy of the given model where all access write and
            specialization relationships have been inverted.
        :rtype: ArchimateModel
        """

        working_copy = copy.deepcopy(model)

        relation_type_key = model.getEdgeAttributeMapping(EdgeAttribute.TYPE)
        relation_source_key = model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        relation_target_key = model.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        relations = (
            relation
            for index, relation in working_copy.edges.iterrows()
            if relation[relation_type_key] in [RelationshipType.ACCESS_WRITE, RelationshipType.SPECIALIZATION]
        )

        for relation in relations:
            source = relation[relation_source_key]
            target = relation[relation_target_key]
            relation[relation_source_key] = target
            relation[relation_target_key] = source
        # END LOOP

        return working_copy

    # END _prepare_model

    @staticmethod
    def _annotate_levels(edges, active, level, visited):
        """
        Annotates a given set of nodes with a hierarchical level based on the given set of edges
        :param list of Edge edges: The edges between the given nodes
        :param list of Node active: The nodes to annotate
        :param number level: The current level
        :param visited: The list of nodes which have been already assigned a level
        :return list of (Node, number): A list of the given nodes annotated by level
        """

        annotated_nodes = []

        # If there are still nodes left to annotate...
        if len(active) > 0:
            for node in active:
                annotated_nodes.append((node, level))
            # END LOOP

            related_targets = list(set(edges[edges.source.isin(active)].target))
            related_targets = [node for node in related_targets if node not in visited]
            visited = visited + related_targets
            annotated_nodes = annotated_nodes + ArchimateMatrixLayout._annotate_levels(
                edges, related_targets, level + 1, visited
            )
        # END IF

        return annotated_nodes

    # END _annotate_levels

    @staticmethod
    def get_coordinates(
        graph,
        width=120,
        height=80,
        max_per_row=8,
        concept_distance=180,
        level_distance=160,
        **kwargs,
    ):
        working_copy = ArchimateMatrixLayout._prepare_model(graph)
        edges = working_copy.edges
        sources = list(set(edges.source))
        targets = list(set(edges.target))
        root = [node for node in sources if node not in targets]
        visited = []

        annotated_nodes = ArchimateMatrixLayout._annotate_levels(edges, root, 0, visited)

        coords = {}
        x = 0
        y = 0
        prev_level = 0

        for node_id, level in annotated_nodes:
            if level != prev_level or x == max_per_row:
                y = y + 1
                x = 0
            # END of if

            array_ = array("f")
            array_.append(x * concept_distance)
            array_.append(y * level_distance)
            coords[node_id] = array_

            x = x + 1
            prev_level = level
        # END of for
        return coords

    # END get_coordinates

    @staticmethod
    def get_name():
        return "matrix"

    # END get_name


# END ArchimateMatrixLayout
