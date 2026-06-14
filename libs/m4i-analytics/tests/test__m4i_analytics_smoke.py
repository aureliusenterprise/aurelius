"""
Smoke tests for m4i-analytics library.

These tests verify that core modules can be imported and basic functionality works.
They serve as a safety net for dependency upgrades (Python version, pandas, numpy, networkx, etc.).
"""


class TestImports:
    """Test that all major modules can be imported without errors."""

    def test_import_graphs_module(self):
        import m4i_analytics.graphs

        assert hasattr(m4i_analytics.graphs, "GraphComplexity")
        assert hasattr(m4i_analytics.graphs, "GraphUtils")

    def test_import_graph_model(self):
        from m4i_analytics.graphs.model.Graph import Graph, NodeAttribute, EdgeAttribute

        assert Graph is not None
        assert NodeAttribute.ID.value == "id"
        assert EdgeAttribute.SOURCE.value == "source"

    def test_import_graph_complexity(self):
        from m4i_analytics.graphs.GraphComplexity import GraphComplexity

        assert hasattr(GraphComplexity, "number_of_nodes")
        assert hasattr(GraphComplexity, "number_of_edges")

    def test_import_graph_utils(self):
        from m4i_analytics.graphs.GraphUtils import GraphUtils

        assert hasattr(GraphUtils, "isValid")
        assert hasattr(GraphUtils, "groupByNodeType")

    def test_import_model_extractor_module(self):
        import m4i_analytics.model_extractor

        assert hasattr(m4i_analytics.model_extractor, "ExtractorLanguagePrimitives")
        assert hasattr(m4i_analytics.model_extractor, "Monitoring")
        assert hasattr(m4i_analytics.model_extractor, "NifiExtractor")
        assert hasattr(m4i_analytics.model_extractor, "Pathing")

    def test_import_m4i_module(self):
        import m4i_analytics.m4i

        assert hasattr(m4i_analytics.m4i, "ApiUtils")
        assert hasattr(m4i_analytics.m4i, "ContentType")
        assert hasattr(m4i_analytics.m4i, "M4IUtils")

    def test_import_content_type_enum(self):
        from m4i_analytics.m4i.ApiUtils import ContentType

        assert ContentType.TEXT.value == "text"
        assert ContentType.JSON.value == "json"
        assert ContentType.BINARY.value == "binary"
        assert ContentType.is_valid("text") is True
        assert ContentType.is_valid("invalid_type") is False


class TestGraphBasics:
    """Test basic Graph functionality with simple data."""

    def test_create_empty_graph(self):
        from m4i_analytics.graphs.model.Graph import Graph

        graph = Graph(id="test-graph")
        assert graph.id == "test-graph"

    def test_create_graph_with_nodes(self):
        import pandas as pd
        from m4i_analytics.graphs.model.Graph import Graph

        nodes = pd.DataFrame(
            {
                "id": ["node1", "node2"],
                "type": ["type_a", "type_b"],
                "name": ["Node 1", "Node 2"],
                "label": ["n1", "n2"],
            }
        )

        graph = Graph(id="test-graph", nodes=nodes)
        assert len(graph.nodes) == 2

    def test_create_graph_with_edges(self):
        import pandas as pd
        from m4i_analytics.graphs.model.Graph import Graph

        nodes = pd.DataFrame(
            {
                "id": ["node1", "node2"],
                "type": ["type_a", "type_b"],
                "name": ["Node 1", "Node 2"],
                "label": ["n1", "n2"],
            }
        )

        edges = pd.DataFrame(
            {
                "id": ["edge1"],
                "source": ["node1"],
                "target": ["node2"],
                "type": ["rel"],
                "name": ["Edge 1"],
                "label": ["e1"],
            }
        )

        graph = Graph(id="test-graph", nodes=nodes, edges=edges)
        assert len(graph.edges) == 1


class TestGraphComplexity:
    """Test GraphComplexity static methods."""

    def test_number_of_nodes(self):
        import pandas as pd
        from m4i_analytics.graphs.GraphComplexity import GraphComplexity
        from m4i_analytics.graphs.model.Graph import Graph

        nodes = pd.DataFrame(
            {
                "id": ["n1", "n2", "n3"],
                "type": ["t", "t", "t"],
                "name": ["a", "b", "c"],
                "label": ["l", "l", "l"],
            }
        )

        graph = Graph(id="test", nodes=nodes)
        assert GraphComplexity.number_of_nodes(graph) == 3

    def test_number_of_edges(self):
        import pandas as pd
        from m4i_analytics.graphs.GraphComplexity import GraphComplexity
        from m4i_analytics.graphs.model.Graph import Graph

        nodes = pd.DataFrame(
            {"id": ["n1", "n2"], "type": ["t", "t"], "name": ["a", "b"], "label": ["l", "l"]}
        )

        edges = pd.DataFrame(
            {
                "id": ["e1", "e2"],
                "source": ["n1", "n1"],
                "target": ["n2", "n2"],
                "type": ["r", "r"],
                "name": ["x", "y"],
                "label": ["l", "l"],
            }
        )

        graph = Graph(id="test", nodes=nodes, edges=edges)
        assert GraphComplexity.number_of_edges(graph) == 2


class TestDependencies:
    """Test that key dependencies are importable and functional."""

    def test_pandas_import(self):
        import pandas as pd

        df = pd.DataFrame({"a": [1, 2, 3]})
        assert len(df) == 3

    def test_networkx_import(self):
        import networkx as nx

        g = nx.DiGraph()
        g.add_node("a")
        g.add_edge("a", "b")
        assert g.number_of_nodes() == 2

    def test_numpy_import(self):
        import numpy as np

        arr = np.array([1, 2, 3])
        assert len(arr) == 3
