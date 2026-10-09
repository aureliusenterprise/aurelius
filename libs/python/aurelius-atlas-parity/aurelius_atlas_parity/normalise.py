"""Normalisation: removing what legitimately differs between two runs (DD-008).

Applied identically to the reference's and the candidate's answers before comparing:

1. remove ignored paths (global rules plus the step's ``ignore``);
2. replace the values of timestamp keys by ``"<timestamp>"``;
3. sort the step's ``unordered`` lists (by content, with GUIDs masked);
4. replace every GUID — in values and in object keys — by ``"<guid-N>"``, numbered by first
   appearance across the whole scenario, so references between answers stay checkable.
"""

import copy
import json
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from aurelius_atlas_parity.paths import locate, transform
from aurelius_atlas_parity.scenario import Step

GUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
TIMESTAMP = "<timestamp>"


class NormalisationRules(BaseModel):
    """Workspace-wide normalisation rules.

    Attributes:
        ignore: Paths removed from every answer.
        timestamps: Object keys whose values are times (replaced at any depth).
    """

    model_config = ConfigDict(frozen=True)

    ignore: tuple[str, ...] = ()
    timestamps: tuple[str, ...] = Field(default=("createTime", "updateTime"))


def load_rules(path: Path) -> NormalisationRules:
    """Read normalisation rules from a YAML file.

    Args:
        path: The file.

    Returns:
        The rules.
    """
    return NormalisationRules.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


class GuidMap:
    """Assigns ``<guid-1>``, ``<guid-2>``, … to GUIDs in order of first appearance."""

    def __init__(self) -> None:
        self._names: dict[str, str] = {}

    def name(self, guid: str) -> str:
        """Return the stable placeholder for a GUID.

        Args:
            guid: A GUID, in any letter case.

        Returns:
            Its placeholder.
        """
        key = guid.lower()
        if key not in self._names:
            self._names[key] = f"<guid-{len(self._names) + 1}>"
        return self._names[key]


def _rename_guids(value: Any, guids: GuidMap) -> Any:  # noqa: ANN401 - any JSON value
    """Return a copy with every GUID string and GUID key replaced, keys visited in sorted order."""
    if isinstance(value, str):
        return guids.name(value) if GUID.match(value) else value
    if isinstance(value, list):
        return [_rename_guids(item, guids) for item in value]
    if isinstance(value, dict):
        renamed = {}
        for key in sorted(value, key=lambda k: (bool(GUID.match(k)), k)):
            new_key = guids.name(key) if GUID.match(key) else key
            renamed[new_key] = _rename_guids(value[key], guids)
        return renamed
    return value


def _mask_guids(value: Any) -> Any:  # noqa: ANN401 - any JSON value
    """Return a copy with every GUID replaced by the same mask, for order-independent sorting."""
    if isinstance(value, str):
        return "<guid>" if GUID.match(value) else value
    if isinstance(value, list):
        return [_mask_guids(item) for item in value]
    if isinstance(value, dict):
        return {("<guid>" if GUID.match(key) else key): _mask_guids(item) for key, item in value.items()}
    return value


def _sorted_list(value: Any) -> Any:  # noqa: ANN401 - any JSON value
    """Sort a list by the canonical JSON of its GUID-masked elements; leave other values."""
    if not isinstance(value, list):
        return value
    return sorted(value, key=lambda item: json.dumps(_mask_guids(item), sort_keys=True))


def normalise(document: Any, rules: NormalisationRules, step: Step, guids: GuidMap) -> Any:  # noqa: ANN401
    """Return a normalised copy of an answer.

    Args:
        document: The parsed answer body.
        rules: Workspace-wide rules.
        step: The step that produced it (its ``ignore`` and ``unordered`` paths).
        guids: The scenario's GUID numbering, shared by all its steps.

    Returns:
        The normalised copy; the input is not changed.
    """
    result = copy.deepcopy(document)
    for path in (*rules.ignore, *step.ignore):
        for container, key in sorted(locate(result, path), key=lambda pair: str(pair[1]), reverse=True):
            del container[key]
    for key in rules.timestamps:
        transform(result, f"$..{key}", lambda _: TIMESTAMP)
    for path in step.unordered:
        transform(result, path, _sorted_list)
    return _rename_guids(result, guids)
