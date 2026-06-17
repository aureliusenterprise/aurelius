"""
Smoke tests for m4i-consistency-metrics backend service.

These tests verify that the Flask application can be imported and basic functionality works.
They serve as a safety net for dependency upgrades (Python version, bokeh, requests-cache).

Note: The Flask app imports m4i_metrics.structural which uses Python 3.10+ union syntax
(pd.DataFrame | None), so most tests are skipped on Python < 3.10.
"""

import sys
import pytest


class TestImports:
    """Test that core modules can be imported without errors."""

    def test_import_flask_app(self):
        if sys.version_info < (3, 10):
            pytest.skip("Flask app imports structural metrics which requires Python 3.10+ union syntax")
        from m4i_consistency_metrics.consistency_metrics import app

        assert app is not None
        assert hasattr(app, "route")

    def test_import_metric_endpoint(self):
        if sys.version_info < (3, 10):
            pytest.skip("metric endpoint imports structural metrics which requires Python 3.10+ union syntax")
        from m4i_consistency_metrics.consistency_metrics import metric

        assert callable(metric)

    def test_import_private_metric_endpoint(self):
        if sys.version_info < (3, 10):
            pytest.skip("private_metric imports structural metrics which requires Python 3.10+ union syntax")
        from m4i_consistency_metrics.consistency_metrics import private_metric

        assert callable(private_metric)

    def test_import_report_module(self):
        if sys.version_info < (3, 10):
            pytest.skip("report module imports structural metrics which requires Python 3.10+ union syntax")
        from m4i_consistency_metrics.report import calculate_metric, generate_metric

        assert callable(calculate_metric)
        assert callable(generate_metric)


class TestFlaskApp:
    """Test Flask application setup."""

    def test_app_has_routes(self):
        if sys.version_info < (3, 10):
            pytest.skip("Flask app imports structural metrics which requires Python 3.10+ union syntax")
        from m4i_consistency_metrics.consistency_metrics import app

        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/metric" in rules
        assert "/private/metric" in rules


class TestDependencies:
    """Test that key dependencies are importable and functional."""

    def test_requests_cache_import(self):
        from requests_cache import install_cache

        assert callable(install_cache)
