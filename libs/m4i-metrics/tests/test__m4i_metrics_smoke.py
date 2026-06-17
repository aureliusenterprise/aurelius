"""
Smoke tests for m4i-metrics library.

These tests verify that core metric modules can be imported and basic functionality works.
They serve as a safety net for dependency upgrades (Python version, pandas, numpy, networkx, bokeh).
"""

import pytest


class TestImports:
    """Test that all major modules can be imported without errors."""

    def test_import_core_classes(self):
        from m4i_metrics import Metric, MetricCategory, MetricColumnConfig, MetricConfig

        assert Metric is not None
        assert MetricCategory is not None
        assert MetricColumnConfig is not None
        assert MetricConfig is not None

    def test_import_physical_metrics(self):
        import m4i_metrics.physical

        assert hasattr(m4i_metrics.physical, "PhysicalMetric")
        assert hasattr(m4i_metrics.physical, "EquipmentAssignedToFacilityMetric")
        assert hasattr(m4i_metrics.physical, "FacilityRelationsMetric")
        assert hasattr(m4i_metrics.physical, "DistributionNetworksMetric")
        assert hasattr(m4i_metrics.physical, "MaterialFlowMetric")

    def test_import_textual_metrics(self):
        import m4i_metrics.textual

        assert hasattr(m4i_metrics.textual, "TextualMetric")
        assert hasattr(m4i_metrics.textual, "ConceptLabelFormattingMetric")
        assert hasattr(m4i_metrics.textual, "LabelAndConceptDuplicationMetric")

    def test_import_structural_metrics(self):
        # NOTE: structural metrics module uses Python 3.10+ union syntax (X | Y)
        # for type hints, which fails on Python < 3.10.
        # This will be fixed during Phase 2 (dependency/compatibility upgrades).
        import sys

        if sys.version_info < (3, 10):
            pytest.skip("structural metrics requires Python 3.10+ union syntax")

        import m4i_metrics.structural

        assert hasattr(m4i_metrics.structural, "StructuralMetric")
        assert hasattr(m4i_metrics.structural, "CycleDetectionMetric")
        assert hasattr(m4i_metrics.structural, "UnconnectedElementsMetric")

    def test_import_process_metrics(self):
        import m4i_metrics.process

        assert hasattr(m4i_metrics.process, "ProcessMetric")
        assert hasattr(m4i_metrics.process, "ActorAndRoleAssignmentMetric")
        assert hasattr(m4i_metrics.process, "ExplicitControlFlowMetric")


class TestMetricBase:
    """Test Metric base class functionality."""

    def test_metric_has_calculate_method(self):
        from m4i_metrics.Metric import Metric

        # Abstract class should have calculate method defined
        assert hasattr(Metric, "calculate")
        assert callable(getattr(Metric, "calculate"))

    def test_metric_get_name(self):
        from m4i_metrics.Metric import Metric

        # Create a concrete implementation for testing
        class TestMetric(Metric):
            metric_label = "test"

            def calculate(self, model):
                return {}

        m = TestMetric()
        assert m.get_name() == "test"


class TestMetricCategory:
    """Test MetricCategory functionality."""

    def test_physical_metric_category(self):
        from m4i_metrics.physical.PhysicalMetric import PhysicalMetric

        assert PhysicalMetric.id is not None
        assert PhysicalMetric.metric_label == "Physical Metrics"
        assert len(PhysicalMetric.metrics) > 0
        assert PhysicalMetric.config is not None


class TestDependencies:
    """Test that key dependencies are importable and functional."""

    def test_pandas_import(self):
        import pandas as pd

        df = pd.DataFrame({"a": [1, 2, 3]})
        assert len(df) == 3

    def test_numpy_import(self):
        import numpy as np

        arr = np.array([1, 2, 3])
        assert len(arr) == 3

    def test_networkx_import(self):
        import networkx as nx

        g = nx.DiGraph()
        g.add_node("a")
        g.add_edge("a", "b")
        assert g.number_of_nodes() == 2
