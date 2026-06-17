"""
Smoke tests for m4i-backend-core library.

These tests verify that core backend utilities can be imported and basic functionality works.
They serve as a safety net for dependency upgrades (Python version, Flask, etc.).
Note: This package already has some unit tests; these smoke tests provide additional coverage.
"""


class TestImports:
    """Test that all major modules can be imported without errors."""

    def test_import_auth_module(self):
        import m4i_backend_core.auth

        assert hasattr(m4i_backend_core.auth, "auth")
        assert hasattr(m4i_backend_core.auth, "requires_auth")
        assert hasattr(m4i_backend_core.auth, "get_token_auth_header")

    def test_import_config_module(self):
        from m4i_backend_core import config

        assert config is not None

    def test_import_shared_module(self):
        from m4i_backend_core.shared import shared

        assert shared is not None

    def test_import_utils_module(self):
        from m4i_backend_core.utils.index_by_property import index_by_property

        assert callable(index_by_property)

    def test_import_auth_model(self):
        from m4i_backend_core.auth.model.AuthError import AuthError

        assert AuthError is not None


class TestUtils:
    """Test utility functions."""

    def test_index_by_property_basic(self):
        from m4i_backend_core.utils.index_by_property import index_by_property

        items = [{"id": "1", "name": "a"}, {"id": "2", "name": "b"}, {"id": "3", "name": "a"}]

        result = index_by_property(items, "name")
        # Function returns {key: single_item} - last item wins for duplicates
        assert "a" in result
        assert "b" in result
        assert result["a"] == {"id": "3", "name": "a"}  # Last 'a' overwrites first
        assert result["b"] == {"id": "2", "name": "b"}

    def test_index_by_property_no_duplicates(self):
        from m4i_backend_core.utils.index_by_property import index_by_property

        items = [{"id": "1", "category": "x"}, {"id": "2", "category": "y"}]

        result = index_by_property(items, "category")
        assert len(result) == 2
        assert result["x"] == {"id": "1", "category": "x"}
        assert result["y"] == {"id": "2", "category": "y"}


class TestAuth:
    """Test auth module basic functionality."""

    def test_requires_auth_is_callable(self):
        from m4i_backend_core.auth.requires_auth import requires_auth

        assert callable(requires_auth)
