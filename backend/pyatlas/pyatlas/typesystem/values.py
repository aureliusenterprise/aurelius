"""Validation / normalisation of attribute values against Atlas types."""
from __future__ import annotations

import datetime as _dt
import math
from typing import Any, Dict, Optional

from ..errors import AtlasBaseException, AtlasErrorCode
from .registry import (CLASSIFICATION, ENTITY, ENUM, FRACTIONAL, INTEGRAL, STRUCT, AttributeInfo, TypeRegistry,
                       parse_type)

_INT_RANGES = {"byte": (-128, 127), "short": (-32768, 32767), "int": (-2**31, 2**31 - 1), "long": (-2**63, 2**63 - 1)}


def _bad(path: str, value: Any, type_name: str):
    raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE, f"{path}={value!r} is not a valid {type_name}")


def parse_date(value: Any, path: str = "date") -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        _bad(path, value, "date")
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            pass
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            d = _dt.datetime.fromisoformat(s)
            if d.tzinfo is None:
                d = d.replace(tzinfo=_dt.timezone.utc)
            return int(d.timestamp() * 1000)
        except ValueError:
            pass
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                d = _dt.datetime.strptime(value, fmt)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=_dt.timezone.utc)
                return int(d.timestamp() * 1000)
            except ValueError:
                continue
    _bad(path, value, "date")
    return None


def normalize_primitive(prim: str, value: Any, path: str) -> Any:
    if value is None:
        return None
    if prim == "string":
        if isinstance(value, (dict, list)):
            _bad(path, value, "string")
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
    if prim == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.lower() in ("true", "false"):
            return value.lower() == "true"
        if isinstance(value, (int, float)) and value in (0, 1):
            return bool(value)
        _bad(path, value, "boolean")
    if prim in INTEGRAL:
        if isinstance(value, bool):
            _bad(path, value, prim)
        try:
            if isinstance(value, float):
                if not value.is_integer():
                    _bad(path, value, prim)
                v = int(value)
            elif isinstance(value, str):
                v = int(float(value)) if "." in value or "e" in value.lower() else int(value)
            else:
                v = int(value)
        except (TypeError, ValueError):
            _bad(path, value, prim)
        rng = _INT_RANGES.get(prim)
        if rng and not (rng[0] <= v <= rng[1]):
            _bad(path, value, prim)
        return v
    if prim in FRACTIONAL:
        if isinstance(value, bool):
            _bad(path, value, prim)
        try:
            v = float(value)
        except (TypeError, ValueError):
            _bad(path, value, prim)
        if math.isnan(v) or math.isinf(v):
            _bad(path, value, prim)
        return v
    if prim == "date":
        return parse_date(value, path)
    _bad(path, value, prim)


def normalize_value(reg: TypeRegistry, type_str: str, value: Any, path: str) -> Any:
    """Normalise ``value`` for Atlas type ``type_str``.

    Entity references are returned untouched (they are resolved by the entity store).
    """
    if value is None:
        return None
    kind, arg = parse_type(type_str)
    if kind == "array":
        if isinstance(value, (list, tuple, set)):
            items = list(value)
        else:
            items = [value]
        return [normalize_value(reg, arg, v, f"{path}[{i}]") for i, v in enumerate(items)]
    if kind == "map":
        if not isinstance(value, dict):
            _bad(path, value, type_str)
        _, vt = arg
        return {str(k): normalize_value(reg, vt, v, f"{path}.{k}") for k, v in value.items()}
    name = arg
    if name in ("byte", "short", "int", "long", "biginteger", "float", "double", "bigdecimal", "boolean", "string", "date"):
        return normalize_primitive(name, value, path)
    if name == "objectid":
        return value
    cat = reg.category_of(name)
    if cat == ENUM:
        et = reg.enums[name]
        if isinstance(value, dict) and "value" in value:
            value = value["value"]
        if isinstance(value, int) and not isinstance(value, bool):
            if value in et.ordinals:
                return et.ordinals[value]
            _bad(path, value, name)
        if isinstance(value, str):
            if value in et.values:
                return value
            for v in et.values:
                if v.lower() == value.lower():
                    return v
        _bad(path, value, name)
    if cat in (STRUCT, CLASSIFICATION):
        return normalize_struct(reg, name, value, path)
    if cat == ENTITY:
        return value
    _bad(path, value, type_str)


def normalize_struct(reg: TypeRegistry, type_name: str, value: Any, path: str) -> dict:
    t = reg.struct_like(type_name)
    if t is None:
        raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, type_name)
    if not isinstance(value, dict):
        _bad(path, value, type_name)
    attrs = value.get("attributes") if "attributes" in value or "typeName" in value else value
    attrs = attrs or {}
    out: Dict[str, Any] = {}
    for k, v in attrs.items():
        a = t.attributes.get(k)
        if a is None:
            continue
        out[k] = normalize_value(reg, a.type_name, v, f"{path}.{k}")
    return {"typeName": type_name, "attributes": out}


def normalize_soft_ref(value: Any, path: str) -> Any:
    """Soft references (``isSoftReference``) are kept as object ids: ``{"guid": .., "typeName": ..}``."""
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        return [normalize_soft_ref(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, dict) and value.get("guid") is None and "typeName" not in value and value:
        return {str(k): normalize_soft_ref(v, f"{path}.{k}") for k, v in value.items()}
    if isinstance(value, dict) and value.get("guid"):
        return {"guid": str(value["guid"]), "typeName": value.get("typeName")}
    if isinstance(value, str) and ":" in value:
        t, g = value.split(":", 1)
        return {"guid": g, "typeName": t}
    _bad(path, value, "soft reference (object id)")


def normalize_attributes(reg: TypeRegistry, attrs_info: Dict[str, AttributeInfo], attrs: Dict[str, Any],
                         type_name: str, check_mandatory: bool, skip: set = frozenset()) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in (attrs or {}).items():
        if k in skip:
            continue
        a = attrs_info.get(k)
        if a is None:
            continue
        if a.is_soft_ref:
            out[k] = normalize_soft_ref(v, f"{type_name}.{k}")
            continue
        out[k] = normalize_value(reg, a.type_name, v, f"{type_name}.{k}")
    if check_mandatory:
        for a in attrs_info.values():
            if a.is_optional or a.is_object_ref or a.is_soft_ref or a.name in skip:
                continue
            v = out.get(a.name)
            if v is None or (isinstance(v, (list, dict)) and a.kind != "simple" and len(v) == 0 and
                             int(a.adef.get("valuesMinCount", 0) or 0) > 0):
                raise AtlasBaseException(AtlasErrorCode.MISSING_MANDATORY_ATTRIBUTE, type_name, a.name)
    return out


def default_for(reg: TypeRegistry, a: AttributeInfo) -> Any:
    dv = a.default_value
    if dv is None or dv == "":
        return None
    try:
        return normalize_value(reg, a.type_name, dv, a.name)
    except AtlasBaseException:
        return None
