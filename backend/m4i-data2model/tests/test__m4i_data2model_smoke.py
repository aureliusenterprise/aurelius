"""
Smoke tests for m4i-data2model backend service.

These tests verify that the Flask application can be imported
and basic functionality works. They serve as a safety net for
dependency upgrades (Python version, pandas, numpy, bokeh).
"""


class TestImports:
    """Test that core modules can be imported without errors."""

    def test_import_flask_app(self):
        from m4i_data2model.data2model import app

        assert app is not None
        assert hasattr(app, "route")

    def test_import_parse_dataset_endpoint(self):
        from m4i_data2model.data2model import parse_dataset

        assert callable(parse_dataset)

    def test_import_extract_endpoint(self):
        from m4i_data2model.data2model import extract

        assert callable(extract)


class TestFlaskApp:
    """Test Flask application setup."""

    def test_app_has_routes(self):
        from m4i_data2model.data2model import app

        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/parse_dataset" in rules
        assert "/extract" in rules


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
