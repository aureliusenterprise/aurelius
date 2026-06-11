from abc import ABCMeta, abstractmethod
from enum import Enum

from networkx.algorithms.shortest_paths.generic import has_path

from m4i_analytics.graphs.GraphUtils import GraphUtils


class AbstractPathingPrimitive:
    __metaclass__ = ABCMeta

    def __init__(self, concept_id):
        self.concept_id = concept_id

    # END __init__

    @abstractmethod
    def filter_model(self, model):
        raise NotImplementedError("Define filter_model to use this pathing primitive!")

    # END apply

    @abstractmethod
    def check_path(self, model, path):
        raise NotImplementedError("Define check_path to use this pathing primitive!")

    # END apply


# END AbstractPathingPrimitive


class StartsWithNodePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        model.edges = model.edges[model.edges.target != self.concept_id]
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[0] == self.concept_id

    # END check_path


# END StartsWithNodePathingPrimitive


class EndsWithNodePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        model.edges = model.edges[model.edges.source != self.concept_id]
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[-1] == self.concept_id

    # END check_path


# END EndsWithNodePathingPrimitive


class PassesNodePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        nx = GraphUtils.toNXGraph(model)
        model.nodes = model.nodes[model.nodes["id"].apply(lambda id: has_path(nx, id, self.concept_id))]
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[-1] == self.concept_id

    # END check_path


# END PassesNodePathingPrimitive


class DoesNotPassNodePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        nx = GraphUtils.toNXGraph(model)
        model.nodes = model.nodes[model.nodes["id"].apply(lambda id: not has_path(nx, id, self.concept_id))]
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[-1] == self.concept_id

    # END check_path


# END DoesNotpassNodePathingPrimitive


class PassesEdgePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        edge = next(model.edges[model.edges["id"] == self.concept_id].iterrows(), None)
        if edge:
            nx = GraphUtils.toNXGraph(model)
            model.nodes = model.nodes[
                model.nodes["id"].apply(
                    lambda id: (
                        has_path(nx, edge["source"], self.concept_id)
                        and has_path(nx, edge["target"], self.concept_id)
                    )
                )
            ]
        # END IF
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[-1] == self.concept_id

    # END check_path


# END PassesEdgePathingPrimitive


class DoesNotPassEdgePathingPrimitive(AbstractPathingPrimitive):
    def filter_model(self, model):
        edge = next(model.edges[model.edges["id"] == self.concept_id].iterrows(), None)
        if edge:
            nx = GraphUtils.toNXGraph(model)
            model.nodes = model.nodes[
                model.nodes["id"].apply(
                    lambda id: (
                        not (
                            has_path(nx, edge["source"], self.concept_id)
                            and has_path(nx, edge["target"], self.concept_id)
                        )
                    )
                )
            ]
        # END IF
        return model

    # END apply

    def check_path(self, model, path):
        return len(path) > 0 and path[-1] == self.concept_id

    # END check_path


# END DoesNotPassEdgePathingPrimitive


class PathingPrimitives(Enum):
    @staticmethod
    def starts_with_node(id):
        return StartsWithNodePathingPrimitive(id)

    # END starts_with_node

    @staticmethod
    def ends_with_node(id):
        return EndsWithNodePathingPrimitive(id)

    # END ends_with_node

    @staticmethod
    def node_in_path(id):
        return PassesNodePathingPrimitive(id)

    # END node_in_path

    @staticmethod
    def node_not_in_path(id):
        return DoesNotPassNodePathingPrimitive(id)

    # END node_not_in_path

    @staticmethod
    def edge_in_path(id):
        return PassesEdgePathingPrimitive(id)

    # END edge_in_path

    @staticmethod
    def edge_not_in_path(id):
        return DoesNotPassNodePathingPrimitive(id)

    # END edge_not_in_path


# END PathingPrimitives
