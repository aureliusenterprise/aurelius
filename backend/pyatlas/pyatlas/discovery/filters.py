"""Translation of Atlas ``SearchParameters.FilterCriteria`` into Elasticsearch queries."""
from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import SYSTEM_ATTR_FIELDS
from ..typesystem.registry import AttributeInfo, TypeRegistry
from ..typesystem.values import parse_date

OPERATOR_ALIASES = {
    "<": "LT", "lt": "LT", ">": "GT", "gt": "GT", "<=": "LTE", "lte": "LTE", ">=": "GTE", "gte": "GTE",
    "=": "EQ", "eq": "EQ", "!=": "NEQ", "neq": "NEQ", "in": "IN", "like": "LIKE",
    "startswith": "STARTS_WITH", "begins_with": "STARTS_WITH", "endswith": "ENDS_WITH", "ends_with": "ENDS_WITH",
    "contains": "CONTAINS", "not_contains": "NOT_CONTAINS", "containsany": "CONTAINS_ANY", "contains_any": "CONTAINS_ANY",
    "containsall": "CONTAINS_ALL", "contains_all": "CONTAINS_ALL", "isnull": "IS_NULL", "is_null": "IS_NULL",
    "notnull": "NOT_NULL", "not_null": "NOT_NULL", "timerange": "TIME_RANGE", "time_range": "TIME_RANGE",
    "notempty": "NOT_EMPTY", "not_empty": "NOT_EMPTY",
}


def normalize_operator(op: Any) -> str:
    s = str(op or "").strip()
    if s.upper() in ("LT", "GT", "LTE", "GTE", "EQ", "NEQ", "IN", "LIKE", "STARTS_WITH", "ENDS_WITH", "CONTAINS",
                     "NOT_CONTAINS", "CONTAINS_ANY", "CONTAINS_ALL", "IS_NULL", "NOT_NULL", "TIME_RANGE", "NOT_EMPTY"):
        return s.upper()
    r = OPERATOR_ALIASES.get(s) or OPERATOR_ALIASES.get(s.lower())
    if r is None:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"unsupported operator {op}")
    return r


def time_range(value: str, now: Optional[_dt.datetime] = None) -> Tuple[int, int]:
    now = now or _dt.datetime.now(_dt.timezone.utc)
    day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)

    def ms(d):
        return int(d.timestamp() * 1000)

    def add_months(d, n):
        m = d.month - 1 + n
        y = d.year + m // 12
        return d.replace(year=y, month=m % 12 + 1, day=1)
    v = str(value).strip().upper()
    month0 = day0.replace(day=1)
    if v == "LAST_7_DAYS":
        s = day0 - _dt.timedelta(days=6)
        return ms(s), ms(s + _dt.timedelta(days=7)) - 1
    if v == "LAST_30_DAYS":
        s = day0 - _dt.timedelta(days=29)
        return ms(s), ms(s + _dt.timedelta(days=30)) - 1
    if v == "TODAY":
        return ms(day0), ms(day0 + _dt.timedelta(days=1)) - 1
    if v == "YESTERDAY":
        s = day0 - _dt.timedelta(days=1)
        return ms(s), ms(day0) - 1
    if v == "THIS_MONTH":
        return ms(month0), ms(add_months(month0, 1)) - 1
    if v == "LAST_MONTH":
        s = add_months(month0, -1)
        return ms(s), ms(month0) - 1
    if v == "THIS_QUARTER":
        s = add_months(month0, -((month0.month - 1) % 3))
        return ms(s), ms(add_months(s, 3)) - 1
    if v == "LAST_QUARTER":
        cur = add_months(month0, -((month0.month - 1) % 3))
        s = add_months(cur, -3)
        return ms(s), ms(cur) - 1
    if v == "LAST_3_MONTHS":
        s = add_months(month0, -3)
        return ms(s), ms(add_months(s, 3)) - 1
    if v == "LAST_6_MONTHS":
        s = add_months(month0, -6)
        return ms(s), ms(add_months(s, 6)) - 1
    if v == "LAST_12_MONTHS":
        s = add_months(month0, -12)
        return ms(s), ms(add_months(s, 12)) - 1
    if v == "THIS_YEAR":
        s = day0.replace(month=1, day=1)
        return ms(s), ms(s.replace(year=s.year + 1)) - 1
    if v == "LAST_YEAR":
        s = day0.replace(year=day0.year - 1, month=1, day=1)
        return ms(s), ms(s.replace(year=s.year + 1)) - 1
    if "," in v:
        a, b = v.split(",", 1)
        return int(parse_date(a.strip())), int(parse_date(b.strip()))
    raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"invalid time range {value}")


class FieldRef:
    def __init__(self, field: str, group: str, has_lc: bool, info: Optional[AttributeInfo] = None, nested: Optional[str] = None):
        self.field = field
        self.group = group
        self.has_lc = has_lc
        self.info = info
        self.nested = nested


REL_SYSTEM_FIELDS = {
    "__guid": ("guid", "str"), "__typeName": ("typeName", "str"), "__state": ("status", "str"),
    "__timestamp": ("createTime", "lng"), "__modificationTimestamp": ("updateTime", "lng"),
    "__createdBy": ("createdBy", "str"), "__modifiedBy": ("updatedBy", "str"), "__label": ("label", "str"),
    "__relationshipLabel": ("label", "str"), "end1Guid": ("end1Guid", "str"), "end2Guid": ("end2Guid", "str"),
}


def resolve_field(reg: TypeRegistry, attr: str, type_names: List[str], scope: str = "entity") -> FieldRef:
    """Map an Atlas attribute name to the ES field holding it."""
    if scope == "relationship":
        if attr in REL_SYSTEM_FIELDS:
            f, g = REL_SYSTEM_FIELDS[attr]
            return FieldRef(f, g, False)
        for t in type_names:
            rt = reg.relationships.get(t)
            a = rt.attribute_defs.get(attr) if rt else None
            if a is not None and a.index_group:
                return FieldRef(f"idx.{a.index_group}.{attr}", a.index_group, a.index_group == "str", a)
        raise AtlasBaseException(AtlasErrorCode.UNKNOWN_ATTRIBUTE, attr, ",".join(type_names) or "relationship")
    if scope == "entity":
        if attr in SYSTEM_ATTR_FIELDS:
            f, g = SYSTEM_ATTR_FIELDS[attr]
            return FieldRef(f, g, False)
        if "." in attr:
            bm, an = attr.split(".", 1)
            bmt = reg.business_metadata.get(bm)
            if bmt and an in bmt.attributes and bmt.attributes[an].index_group:
                a = bmt.attributes[an]
                return FieldRef(f"bmidx.{a.index_group}.{bm}.{an}", a.index_group, a.index_group == "str", a)
        a = None
        for t in type_names:
            et = reg.entities.get(t)
            if et and attr in et.attributes:
                a = et.attributes[attr]
                break
        if a is None:
            a = reg.find_attribute_any_type(attr)
        if a is None or a.index_group is None:
            raise AtlasBaseException(AtlasErrorCode.UNKNOWN_ATTRIBUTE, attr, ",".join(type_names) or "entity")
        return FieldRef(f"idx.{a.index_group}.{attr}", a.index_group, a.index_group == "str", a)
    # classification attributes live in the nested "tags" field
    if attr == "__typeName":
        return FieldRef("tags.typeName", "str", False, nested="tags")
    a = None
    for t in type_names:
        ct = reg.classifications.get(t)
        if ct and attr in ct.attributes:
            a = ct.attributes[attr]
            break
    if a is None:
        for ct in reg.classifications.values():
            if attr in ct.attributes and ct.attributes[attr].index_group:
                a = ct.attributes[attr]
                break
    if a is None or a.index_group is None:
        raise AtlasBaseException(AtlasErrorCode.UNKNOWN_ATTRIBUTE, attr, ",".join(type_names) or "classification")
    return FieldRef(f"tags.idx.{a.index_group}.{attr}", a.index_group, a.index_group == "str", a, nested="tags")


def _coerce(ref: FieldRef, v: Any) -> Any:
    if v is None:
        return None
    if ref.group == "lng":
        if ref.info is not None and ref.info.base == "date":
            return parse_date(v)
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return parse_date(v)
    if ref.group == "dbl":
        return float(v)
    if ref.group == "bool":
        return v if isinstance(v, bool) else str(v).lower() == "true"
    return str(v)


def _split_values(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    s = str(v).strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
    return [x.strip().strip('"').strip("'") for x in s.split(",") if x.strip()]


def leaf_query(ref: FieldRef, op: str, value: Any, case_insensitive_eq: bool = True) -> dict:
    op = normalize_operator(op)
    f = ref.field
    is_str = ref.group == "str"
    lc = f + ".lc" if (is_str and ref.has_lc) else f
    if not case_insensitive_eq and op in ("EQ", "NEQ", "IN", "CONTAINS_ANY", "CONTAINS_ALL"):
        return leaf_query(FieldRef(f, ref.group, False, ref.info, ref.nested), op, value)

    def lcv(x):
        return str(x).lower() if (is_str and ref.has_lc) else x

    if op == "IS_NULL":
        return {"bool": {"must_not": [{"exists": {"field": f}}]}}
    if op == "NOT_NULL":
        return {"exists": {"field": f}}
    if op == "NOT_EMPTY":
        q = {"bool": {"filter": [{"exists": {"field": f}}]}}
        if is_str:
            q["bool"]["must_not"] = [{"term": {f: ""}}]
        return q
    if op == "TIME_RANGE":
        a, b = time_range(value)
        return {"range": {f: {"gte": a, "lte": b}}}
    if op in ("IN", "CONTAINS_ANY"):
        vals = [_coerce(ref, x) for x in _split_values(value)]
        return {"terms": {lc: [lcv(x) for x in vals]}}
    if op == "CONTAINS_ALL":
        vals = [_coerce(ref, x) for x in _split_values(value)]
        return {"bool": {"filter": [{"term": {lc: lcv(x)}} for x in vals]}}
    v = _coerce(ref, value)
    if op == "EQ":
        return {"term": {lc: lcv(v)}}
    if op == "NEQ":
        return {"bool": {"must_not": [{"term": {lc: lcv(v)}}]}}
    if op in ("LT", "GT", "LTE", "GTE"):
        return {"range": {f: {op.lower(): v}}}
    if not is_str:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"operator {op} is only valid for string attributes")
    sv = _escape_wildcard(str(v).lower())
    if op == "LIKE":
        pat = str(v).lower().replace("%", "*")
        return {"wildcard": {lc: {"value": pat, "case_insensitive": True}}}
    if op == "STARTS_WITH":
        return {"prefix": {lc: {"value": str(v).lower(), "case_insensitive": True}}}
    if op == "ENDS_WITH":
        return {"wildcard": {lc: {"value": "*" + sv, "case_insensitive": True}}}
    if op == "CONTAINS":
        return {"wildcard": {lc: {"value": "*" + sv + "*", "case_insensitive": True}}}
    if op == "NOT_CONTAINS":
        return {"bool": {"must_not": [{"wildcard": {lc: {"value": "*" + sv + "*", "case_insensitive": True}}}]}}
    raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"unsupported operator {op}")


def _escape_wildcard(s: str) -> str:
    return s.replace("\\", "\\\\").replace("*", "\\*").replace("?", "\\?")


def criteria_query(reg: TypeRegistry, criteria: Optional[dict], type_names: List[str], scope: str = "entity") -> Optional[dict]:
    if not criteria:
        return None
    if criteria.get("criterion"):
        subs = [criteria_query(reg, c, type_names, scope) for c in criteria["criterion"]]
        subs = [s for s in subs if s]
        if not subs:
            return None
        cond = str(criteria.get("condition") or "AND").upper()
        if cond == "OR":
            return {"bool": {"should": subs, "minimum_should_match": 1}}
        return {"bool": {"filter": subs}}
    attr = criteria.get("attributeName")
    if not attr:
        return None
    if scope != "entity" and attr.startswith("__") and attr != "__typeName":
        return None  # other classification system attributes are not tracked per tag
    ref = resolve_field(reg, attr, type_names, scope)
    return leaf_query(ref, criteria.get("operator") or "EQ", criteria.get("attributeValue"))
