import ast
from pathlib import Path

import pytest
from aurelius_atlas_testing.inventory import ApiItem, inventory, is_public, items_in_module, module_name

SOURCE = """
def public(): ...
async def public_async(): ...
def _private(): ...

class Data:
    x: int

class Error(Exception):
    pass

class Validated:
    def _check(self): ...

class Service:
    def run(self): ...
    async def run_async(self): ...
    @property
    def size(self): ...
    def _helper(self): ...
    def __eq__(self, other): ...

class _Hidden:
    def run(self): ...
"""


@pytest.mark.covers("aurelius_atlas_testing.inventory.items_in_module", rules=["TRC-04"])
def test__items_in_module_lists_public_behaviour() -> None:
    """Public functions and members are listed; data classes and private names are not."""
    items = items_in_module(ast.parse(SOURCE), "pkg.mod", "pkg/mod.py")

    assert [(item.target, item.kind) for item in items] == [
        ("pkg.mod.public", "function"),
        ("pkg.mod.public_async", "function"),
        ("pkg.mod.Validated", "class"),
        ("pkg.mod.Service.run", "method"),
        ("pkg.mod.Service.run_async", "method"),
        ("pkg.mod.Service.size", "property"),
    ]
    assert items[0] == ApiItem(target="pkg.mod.public", kind="function", path="pkg/mod.py", line=2)


@pytest.mark.covers("aurelius_atlas_testing.inventory.is_public", rules=["TRC-04"])
@pytest.mark.parametrize(("name", "public"), [("run", True), ("_run", False), ("__init__", False), ("__main__", False)])
def test__is_public(name: str, public: bool) -> None:  # noqa: FBT001
    """Names starting with an underscore are private."""
    assert is_public(name) is public


@pytest.mark.covers("aurelius_atlas_testing.inventory.module_name")
def test__module_name(tmp_path: Path) -> None:
    """Files map to dotted module names; __init__ maps to its package."""
    package = tmp_path / "pkg"

    assert module_name(package, package / "__init__.py") == "pkg"
    assert module_name(package, package / "sub" / "mod.py") == "pkg.sub.mod"


@pytest.mark.covers("aurelius_atlas_testing.inventory.inventory", rules=["TRC-04"])
def test__inventory_walks_package_and_skips_private_modules(tmp_path: Path) -> None:
    """Every public module is read; private modules and __main__ are skipped; results are sorted."""
    package = tmp_path / "pkg"
    (package / "sub").mkdir(parents=True)
    (package / "__init__.py").write_text("def top(): ...\n")
    (package / "sub" / "__init__.py").write_text("")
    (package / "sub" / "zeta.py").write_text("def z(): ...\n")
    (package / "alpha.py").write_text("def a(): ...\n")
    (package / "_internal.py").write_text("def hidden(): ...\n")
    (package / "__main__.py").write_text("def entry(): ...\n")

    assert [item.target for item in inventory(package)] == ["pkg.alpha.a", "pkg.sub.zeta.z", "pkg.top"]
