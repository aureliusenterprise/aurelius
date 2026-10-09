import sys
from pathlib import Path

import pytest

pytest_plugins = ["pytester"]
if "aurelius_atlas_testing.plugin" not in sys.modules:
    # Run from this project, the entry point is disabled (pyproject addopts) so that coverage
    # measures the plugin's import; load it here instead. Run from the workspace root, the
    # entry point has already loaded it.
    pytest_plugins.append("aurelius_atlas_testing.plugin")


@pytest.fixture
def workspace_root() -> Path:
    """Return the root of the real workspace this library lives in."""
    return Path(__file__).resolve().parents[4]
