from m4i_graphviz_layouts.HierarchicalLayout import HierarchicalLayout

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import RelationshipType
from m4i_analytics.graphs.model.Graph import EdgeAttribute

import copy


class ArchimateProcessLayout(HierarchicalLayout):

    @staticmethod
    def _prepare_model(model):

        """
        Prepares a model for the hierarchical layout visualization by inverting all access writes and specialization relations
        :param ArchimateModel model: the model that should be prepared
        :return ArchimateModel: A copy of the given model where all access write and specialization relationships have been inverted
        """

        working_copy = copy.deepcopy(model)

        relation_type_key = model.getEdgeAttributeMapping(EdgeAttribute.TYPE)
        relation_source_key = model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        relation_target_key = model.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        relations = (relation for index, relation in working_copy.edges.iterrows()
                     if relation[relation_type_key] in [RelationshipType.ACCESS_WRITE, RelationshipType.SPECIALIZATION])

        for relation in relations:
            source = relation[relation_source_key]
            target = relation[relation_target_key]
            relation[relation_source_key] = target
            relation[relation_target_key] = source
        # END LOOP

        return working_copy
    # END _prepare_model

    @staticmethod
    def get_coordinates(model, dpi=80, rankdir='LR', nodesep=0.5, ranksep=0.5, node_width=0.1, node_height=0.1, **kwargs):
        prepared_model = ArchimateProcessLayout._prepare_model(model)
        return HierarchicalLayout.get_coordinates(prepared_model, dpi, rankdir, nodesep, ranksep, node_width, node_height, **kwargs)
    # END get_coordinates

    @staticmethod
    def get_name():
        return 'archimate_process'
    # END get_name

# END ArchimateProcessLayout