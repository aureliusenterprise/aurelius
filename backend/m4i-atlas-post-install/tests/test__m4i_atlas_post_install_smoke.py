"""
Smoke tests for m4i-atlas-post-install library.

These tests verify that core modules can be imported and basic functionality works.
They serve as a safety net for dependency upgrades (Python version, urllib3, elasticsearch).
"""


class TestImports:
    """Test that all major modules can be imported without errors."""

    def test_import_main_module(self):
        import m4i_atlas_post_install

        assert hasattr(m4i_atlas_post_install, "engines")
        assert hasattr(m4i_atlas_post_install, "cleanup")
        assert hasattr(m4i_atlas_post_install, "drop_non_entities")
        assert hasattr(m4i_atlas_post_install, "extract")
        assert hasattr(m4i_atlas_post_install, "index_entities")
        assert hasattr(m4i_atlas_post_install, "update_types")
        assert hasattr(m4i_atlas_post_install, "get_all_documents")
        assert hasattr(m4i_atlas_post_install, "get_enterprise_search_key")
        assert hasattr(m4i_atlas_post_install, "index_all_documents")
        assert hasattr(m4i_atlas_post_install, "load_documents")
        assert hasattr(m4i_atlas_post_install, "index_documents")
        assert hasattr(m4i_atlas_post_install, "publish_state_template")

    def test_import_app_search_engine_setup(self):
        from m4i_atlas_post_install.app_search_engine_setup import engines

        assert engines is not None

    def test_import_export_diff(self):
        from m4i_atlas_post_install.export_diff import (
            cleanup,
            drop_non_entities,
            extract,
            index_entities,
            update_types,
        )

        assert callable(cleanup)
        assert callable(drop_non_entities)
        assert callable(extract)
        assert callable(index_entities)
        assert callable(update_types)

    def test_import_documents_utils(self):
        from m4i_atlas_post_install.documents_utils import load_documents, index_documents

        assert callable(load_documents)
        assert callable(index_documents)

    def test_import_index_template(self):
        from m4i_atlas_post_install.index_template import publish_state_template

        assert publish_state_template is not None


class TestDependencies:
    """Test that key dependencies are importable and functional."""

    def test_elasticsearch_import(self):
        import elasticsearch

        assert hasattr(elasticsearch, "Elasticsearch")

    def test_urllib3_import(self):
        import urllib3

        # Basic functionality check
        pool = urllib3.PoolManager()
        assert pool is not None
