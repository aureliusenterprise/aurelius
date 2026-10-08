"""
Griffe extension for documentation builds.

Extends `griffe_pydantic` so that models whose base classes don't resolve
statically are still recognized as Pydantic models:

- `sqlmodel.SQLModel` subclasses (SQLModel tables such as `Entity`)
- `pydantic_settings.BaseSettings` subclasses (application settings models)

Both inherit from `pydantic.BaseModel` at runtime, but griffe's static
analysis can't resolve those third-party bases (the packages aren't loaded
statically), so griffe-pydantic's `_inherits_pydantic` check misses them.
This extension widens the check with a small allowlist of extra base paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from griffe_pydantic import PydanticExtension
from griffe_pydantic._internal import static

if TYPE_CHECKING:
    from griffe import Attribute, Class, Module

_EXTRA_BASES: frozenset[str] = frozenset(
    {
        "pydantic_settings.BaseSettings",
        "pydantic_settings.main.BaseSettings",
        "sqlmodel.SQLModel",
        "sqlmodel.main.SQLModel",
    }
)


class AureliusPydanticExtension(PydanticExtension):
    """Recognize SQLModel and BaseSettings models as Pydantic models."""

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:
        """Process the package with an widened base-class check."""
        orig = static._inherits_pydantic

        def _inherits(cls: Class) -> bool:
            return orig(cls) or any(getattr(base, "canonical_path", base) in _EXTRA_BASES for base in cls.bases)

        static._inherits_pydantic = _inherits
        try:
            super().on_package(pkg=pkg, **kwargs)
        finally:
            static._inherits_pydantic = orig
        self._strip_non_fields(pkg)

    def _strip_non_fields(self, mod: Module) -> None:
        """Remove the pydantic-field label from non-field members.

        ``griffe_pydantic`` labels every attribute of a detected model as a
        field, but SQLModel table classes carry SQLAlchemy attributes
        (``__mapper_args__`` etc.) without annotations, which break the
        pydantic-model template.
        """
        for cls in mod.classes.values():
            fields = cls.extra.get("griffe_pydantic", {}).get("fields")
            if callable(fields):
                model_fields: dict[str, Attribute] = fields()  # pyright: ignore[reportAssignmentType]
                for attr in model_fields.values():
                    if attr.annotation is None:
                        attr.labels.discard("pydantic-field")
        for submodule in mod.modules.values():
            if not submodule.is_alias:
                self._strip_non_fields(submodule)
