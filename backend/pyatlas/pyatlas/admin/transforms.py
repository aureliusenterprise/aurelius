"""Import-time entity transformations (Atlas ``ImportTransforms`` and ``entitytransform``).

Two import options are supported, both are JSON strings exactly as in Apache Atlas:

``transforms`` (``ImportTransforms``)
    ``{"<typeName>": {"<attribute>|*": ["<transformer>", ...]}}`` applied to entities of that type and
    its sub types.  Transformers (parameters separated by ``~``)::

        replace~<find>~<replaceWith>    lowercase    uppercase           (string attribute values)
        clearAttrValue~<attr1>,<attr2>  add~<attr>=<value>|list:<value>  setDeleted
        addClassification~<name>[~topLevel]         removeClassification~<name>       (entity level, key "*")

``transformers`` (``AtlasEntityTransformer`` / ``BaseEntityHandler``)
    ``[{"conditions": {"<attr>": "<COND>:<value>"}, "action": {"<attr>": "<ACTION>:<value>"}}]`` where
    attribute keys may be qualified by type (``hive_table.name``).  Conditions: ``EQUALS`` (default),
    ``EQUALS_IGNORE_CASE``, ``STARTS_WITH``, ``STARTS_WITH_IGNORE_CASE``, ``HAS_VALUE``, ``__entity``
    with ``TOPLEVEL`` / ``ALL`` / ``OBJECTID``.  Actions: ``SET`` (default), ``REPLACE_PREFIX``,
    ``TO_LOWER``, ``TO_UPPER``, ``CLEAR``, ``ADD_CLASSIFICATION``.  The virtual attributes
    ``hive_db.name``, ``hive_db.clusterName``, ``hive_table.name``, ``hive_column.name``,
    ``hive_storagedesc.location``, ``hdfs_path.name``, ``hdfs_path.path`` and ``hdfs_path.clusterName``
    rename Hive / HDFS entities and rebuild their qualifiedName, like Atlas' entity handlers.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Set

from ..errors import AtlasBaseException, AtlasErrorCode

SEP = "~"


def _load_json(raw: Any):
    if raw is None or raw == "":
        return None
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except ValueError as e:
        raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE, f"invalid transforms JSON: {e}")


def _matches_object_id(oid: dict, entity: dict) -> bool:
    if oid.get("guid"):
        return oid["guid"] == entity.get("guid")
    if oid.get("typeName") != entity.get("typeName"):
        return False
    attrs = entity.get("attributes") or {}
    return all(attrs.get(k) == v for k, v in (oid.get("uniqueAttributes") or {}).items())


# =========================================================================== "transforms"
class _Transformer:
    def __init__(self, kind: str, fn: Callable[[Any], Any], classification: Optional[str] = None,
                 top_level: bool = False):
        self.kind = kind
        self.fn = fn
        self.classification = classification
        self.top_level = top_level
        self.filters: List[dict] = []

    def apply(self, value: Any) -> Any:
        return self.fn(self, value)


def _replace(find: str, repl: str):
    return lambda t, v: v.replace(find, repl) if isinstance(v, str) and find else v


def _add_classification(t: _Transformer, e: Any):
    if not isinstance(e, dict):
        return e
    if t.top_level and not any(_matches_object_id(f, e) for f in t.filters):
        return e
    if e.get("classifications") is None:
        e["classifications"] = []
    cls = e["classifications"]
    if not any(c.get("typeName") == t.classification for c in cls):
        cls.append({"typeName": t.classification, "attributes": {}})
    return e


def _remove_classification(t: _Transformer, e: Any):
    if isinstance(e, dict) and e.get("classifications"):
        e["classifications"] = [c for c in e["classifications"] if c.get("typeName") != t.classification]
    return e


def _add_value(name_value: str):
    if "=" not in name_value:
        return lambda t, e: e
    attr, raw = name_value.split("=", 1)
    value: Any = [raw[len("list:"):]] if raw.startswith("list:") else raw

    def fn(t, e):
        if not isinstance(e, dict):
            return e
        attrs = e.setdefault("attributes", {})
        cur = attrs.get(attr)
        if cur is None:
            attrs[attr] = value
        elif isinstance(cur, list):
            cur.extend(value if isinstance(value, list) else [value])
        else:
            attrs[attr] = raw
        return e
    return fn


def _clear_attrs(names: str):
    attrs_to_clear = [n for n in names.split(",") if n]

    def fn(t, e):
        if isinstance(e, dict):
            for n in attrs_to_clear:
                (e.setdefault("attributes", {}))[n] = None
        return e
    return fn


def _set_deleted(t, e):
    if isinstance(e, dict):
        e["status"] = "DELETED"
    return e


def make_transformer(spec: str) -> _Transformer:
    if ":" in spec and SEP not in spec:
        raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE,
                                 "Invalid transformer specification. The parameter separator ':' is no longer supported. "
                                 f"Use '~' instead. Transformer specification: {spec}")
    params = [p for p in spec.split(SEP)]
    key = params[0] if params else spec
    rest = SEP.join(params[1:])
    if key == "replace":
        return _Transformer(key, _replace(params[1] if len(params) > 1 else "", params[2] if len(params) > 2 else ""))
    if key == "lowercase":
        return _Transformer(key, lambda t, v: v.lower() if isinstance(v, str) else v)
    if key == "uppercase":
        return _Transformer(key, lambda t, v: v.upper() if isinstance(v, str) else v)
    if key == "removeClassification":
        return _Transformer(key, _remove_classification, classification=rest)
    if key == "add":
        return _Transformer(key, _add_value(rest))
    if key == "clearAttrValue":
        return _Transformer(key, _clear_attrs(rest))
    if key == "setDeleted":
        return _Transformer(key, _set_deleted)
    if key == "addClassification":
        return _Transformer(key, _add_classification, classification=params[1] if len(params) > 1 else "",
                            top_level=len(params) == 3 and params[2] == "topLevel")
    raise AtlasBaseException(AtlasErrorCode.INVALID_VALUE, f"Error creating ImportTransformer. Unknown transformer: {spec}.")


class ImportTransforms:
    ALL = "*"

    def __init__(self, spec: Dict[str, Dict[str, List[str]]]):
        self.transforms: Dict[str, Dict[str, List[_Transformer]]] = {}
        for type_name, attr_map in (spec or {}).items():
            for attr, specs in (attr_map or {}).items():
                for s in specs or []:
                    try:
                        t = make_transformer(s)
                    except AtlasBaseException:
                        continue  # Atlas logs and skips invalid transformers
                    self.transforms.setdefault(type_name, {}).setdefault(attr, []).append(t)

    @classmethod
    def from_option(cls, raw: Any) -> Optional["ImportTransforms"]:
        spec = _load_json(raw)
        return cls(spec) if spec else None

    def shape(self, registry, export_items: List[dict], create_classification) -> None:
        """``ImportTransformsShaper``: top-level filters, missing classification defs, sub types."""
        for attr_map in self.transforms.values():
            for lst in attr_map.values():
                for t in lst:
                    if t.kind == "addClassification":
                        t.filters = list(export_items or [])
                        create_classification(t.classification)
        for type_name in list(self.transforms):
            et = registry.entities.get(type_name)
            if et is None:
                continue
            parent = self.transforms[type_name]
            for sub in et.type_and_all_sub_types() - {type_name}:
                if sub not in self.transforms:
                    self.transforms[sub] = parent
                else:
                    for attr, lst in parent.items():
                        if attr in self.transforms[sub]:
                            self.transforms[sub][attr].extend(lst)

    def classifications_to_create(self) -> Set[str]:
        return {t.classification for m in self.transforms.values() for lst in m.values() for t in lst
                if t.kind == "addClassification" and t.classification}

    def apply(self, entity: dict) -> dict:
        m = self.transforms.get(entity.get("typeName"))
        if not m:
            return entity
        for t in m.get(self.ALL, []):
            t.apply(entity)
        attrs = entity.setdefault("attributes", {})
        for attr, lst in m.items():
            if attr == self.ALL or attr not in attrs:
                continue
            v = attrs[attr]
            for t in lst:
                v = t.apply(v)
            attrs[attr] = v
        return entity


# =========================================================================== "transformers"
class EntityAttribute:
    def __init__(self, key: str, registry):
        self.key = key.strip()
        self.types: Optional[Set[str]] = None
        if "." in self.key:
            tname, self.name = self.key.split(".", 1)
            et = registry.entities.get(tname.strip()) if registry is not None else None
            self.types = et.type_and_all_sub_types() if et is not None else None
            self.name = self.name.strip()
        else:
            self.name = self.key

    def applies_to(self, type_name: str) -> bool:
        return self.types is None or not type_name or type_name in self.types


class TransformableEntity:
    """``AtlasTransformableEntity`` plus the Hive / HDFS handlers' virtual attributes."""

    VIRTUAL: Dict[str, Set[str]] = {
        "hive_db": {"hive_db.name", "hive_db.clusterName"},
        "hive_table": {"hive_db.name", "hive_table.name", "hive_db.clusterName"},
        "hive_column": {"hive_db.name", "hive_table.name", "hive_column.name", "hive_db.clusterName"},
        "hive_storagedesc": {"hive_db.name", "hive_table.name", "hive_db.clusterName", "hive_storagedesc.location"},
        "hdfs_path": {"hdfs_path.name", "hdfs_path.path", "hdfs_path.clusterName"},
    }

    def __init__(self, entity: dict, handler: Optional[str]):
        self.entity = entity
        self.handler = handler
        self.v: Dict[str, Any] = {}
        self.updated = False
        self.path_updated = False
        a = entity.get("attributes") or {}
        qn = a.get("qualifiedName")
        t = handler
        if t == "hive_db":
            self.v = {"hive_db.name": a.get("name"), "hive_db.clusterName": qn[qn.rfind("@") + 1:] if qn and "@" in qn else ""}
        elif t == "hive_table":
            db = cl = tq = ""
            if qn:
                i, j = qn.find("."), qn.rfind("@")
                db = qn[:i] if i != -1 else ""
                cl = qn[j + 1:] if j != -1 else ""
                tq = qn[i + 1:j] if j != -1 else ""
            self.table_name_from_qn = tq
            self.table_name_differs = bool(qn) and tq != a.get("name")
            self.v = {"hive_table.name": a.get("name"), "hive_db.name": db, "hive_db.clusterName": cl}
        elif t == "hive_column":
            db = tb = cl = ""
            if qn:
                i = qn.find(".")
                k = qn.find(".", i + 1) if i != -1 else -1
                j = qn.rfind("@")
                db = qn[:i].strip() if i != -1 else ""
                tb = qn[i + 1:k].strip() if k != -1 else ""
                cl = qn[j + 1:].strip() if j != -1 else ""
            self.v = {"hive_db.name": db, "hive_table.name": tb, "hive_column.name": a.get("name"),
                      "hive_db.clusterName": cl}
        elif t == "hive_storagedesc":
            db = tb = cl = ""
            if qn:
                i, j = qn.find("."), qn.rfind("@")
                cws = qn[j + 1:] if j != -1 else ""
                db = qn[:i] if i != -1 else ""
                tb = qn[i + 1:j] if i != -1 and j != -1 else ""
                k = cws.rfind("_storage")
                cl = cws[:k] if k != -1 else ""
            self.v = {"hive_db.name": db, "hive_table.name": tb, "hive_db.clusterName": cl,
                      "hive_storagedesc.location": a.get("location")}
        elif t == "hdfs_path":
            path, name = a.get("path"), a.get("name")
            cl, prefix = "", ""
            if qn:
                j = qn.rfind("@")
                cl = qn[j + 1:] if j != -1 else ""
                if path and name and name in path:
                    prefix = path[:path.find(name)]
            self.path_prefix = prefix
            self.v = {"hdfs_path.clusterName": cl, "hdfs_path.name": name, "hdfs_path.path": path}

    def get(self, attr: EntityAttribute) -> Any:
        if attr.key in self.v:
            return self.v[attr.key]
        if attr.applies_to(self.entity.get("typeName")):
            return (self.entity.get("attributes") or {}).get(attr.name)
        return None

    def set(self, attr: EntityAttribute, value: Any) -> None:
        if attr.key in self.v:
            self.v[attr.key] = value
            if attr.key == "hive_storagedesc.location":
                self.entity.setdefault("attributes", {})["location"] = value
                return
            self.updated = True
            if attr.key == "hdfs_path.path":
                self.path_updated = True
            return
        if attr.applies_to(self.entity.get("typeName")):
            self.entity.setdefault("attributes", {})[attr.name] = value

    def complete(self) -> None:
        if not self.updated:
            return
        a = self.entity.setdefault("attributes", {})
        v, t = self.v, self.handler
        if t == "hive_db":
            a["name"], a["clusterName"] = v["hive_db.name"], v["hive_db.clusterName"]
            a["qualifiedName"] = f"{v['hive_db.name']}@{v['hive_db.clusterName']}"
        elif t == "hive_table":
            a["name"] = v["hive_table.name"]
            tn = self.table_name_from_qn if self.table_name_differs else v["hive_table.name"]
            a["qualifiedName"] = f"{v['hive_db.name']}.{tn}@{v['hive_db.clusterName']}"
        elif t == "hive_column":
            a["name"] = v["hive_column.name"]
            a["qualifiedName"] = f"{v['hive_db.name']}.{v['hive_table.name']}.{v['hive_column.name']}@{v['hive_db.clusterName']}"
        elif t == "hive_storagedesc":
            loc = v.get("hive_storagedesc.location")
            i = loc.rfind("/") if isinstance(loc, str) else -1
            a["location"] = loc[:i] + "/" + v["hive_table.name"] if i != -1 else loc
            a["qualifiedName"] = f"{v['hive_db.name']}.{v['hive_table.name']}@{v['hive_db.clusterName']}_storage"
        elif t == "hdfs_path":
            path = v["hdfs_path.path"] if self.path_updated else (self.path_prefix + (v["hdfs_path.name"] or "")
                                                                  if self.path_prefix else v["hdfs_path.name"])
            a["clusterName"], a["name"], a["path"] = v["hdfs_path.clusterName"], v["hdfs_path.name"], path
            a["qualifiedName"] = f"{path}@{v['hdfs_path.clusterName']}" if v["hdfs_path.clusterName"] else path


def _condition(key: str, value: Optional[str], registry, export_items: List[dict]):
    value = value if value is None else str(value)
    i = value.find(":") if value is not None else -1
    name = (value[:i] if i != -1 else "EQUALS").strip().upper()
    cval = (value[i + 1:] if i != -1 else value)
    cval = cval.strip() if cval is not None else None
    attr = EntityAttribute(key, registry)

    def s(e):
        v = e.get(attr)
        return None if v is None else str(v)
    if name == "ALL":
        return lambda e: True
    if name in ("TOPLEVEL", "OBJECTID"):
        return lambda e: any(_matches_object_id(o, e.entity) for o in export_items or [])
    if name == "EQUALS":
        return lambda e: s(e) is not None and s(e) == cval
    if name == "EQUALS_IGNORE_CASE":
        return lambda e: s(e) is not None and cval is not None and s(e).lower() == cval.lower()
    if name == "STARTS_WITH":
        return lambda e: s(e) is not None and cval is not None and s(e).startswith(cval)
    if name == "STARTS_WITH_IGNORE_CASE":
        return lambda e: s(e) is not None and cval is not None and s(e).lower().startswith(cval.lower())
    if name == "HAS_VALUE":
        return lambda e: bool(s(e))
    full = value.strip() if value is not None else None
    return lambda e: s(e) is not None and s(e) == full


def _action(key: str, value: Optional[str], registry, create_classification):
    value = value if value is None else str(value)
    i = value.find(":") if value is not None else -1
    name = (value[:i] if i != -1 else "SET").strip().upper()
    aval = (value[i + 1:] if i != -1 else value)
    aval = aval.strip() if aval is not None else None
    attr = EntityAttribute(key, registry)
    if name == "ADD_CLASSIFICATION":
        create_classification(aval)

        def add_cls(e):
            cls = e.entity.get("classifications")
            if cls is None:
                cls = e.entity["classifications"] = []
            if not any(c.get("typeName") == aval for c in cls):
                cls.append({"typeName": aval, "attributes": {}})
        return attr, add_cls
    if name == "REPLACE_PREFIX":
        frm, to = None, ""
        if aval is not None:
            j = aval.find(":")
            if j == -1:
                frm = aval
            else:
                sep = aval[:j].strip()
                k = aval.find(sep, j + 1) if sep else -1
                if k == -1:
                    frm = aval[j + 1:]
                else:
                    frm, to = aval[j + 1:k], aval[k + len(sep):]

        def repl(e):
            cur = e.get(attr)
            if frm and cur is not None and str(cur).startswith(frm):
                e.set(attr, str(cur).replace(frm, to, 1))
        return attr, repl
    if name == "TO_LOWER":
        return attr, lambda e: e.set(attr, e.get(attr).lower()) if isinstance(e.get(attr), str) else None
    if name == "TO_UPPER":
        return attr, lambda e: e.set(attr, e.get(attr).upper()) if isinstance(e.get(attr), str) else None
    if name == "CLEAR":
        return attr, lambda e: e.set(attr, None) if e.get(attr) is not None else None
    if name == "SET":
        return attr, lambda e: e.set(attr, aval)
    full = value.strip() if value is not None else None
    return attr, lambda e: e.set(attr, full)


class EntityTransformers:
    def __init__(self, spec: List[dict], registry, export_items: List[dict], create_classification):
        self.rules = []
        keys: Set[str] = set()
        for r in spec or []:
            if not isinstance(r, dict):
                continue
            conds = [_condition(k, v, registry, export_items) for k, v in (r.get("conditions") or {}).items()]
            acts = [_action(k, v, registry, create_classification) for k, v in (r.get("action") or {}).items()]
            keys |= {a.key for a, _ in acts}
            self.rules.append((conds, [f for _, f in acts]))
        # which handlers are needed (BaseEntityHandler.createEntityHandlers)
        self.handlers = [t for t, virt in TransformableEntity.VIRTUAL.items() if virt & keys]

    @classmethod
    def from_option(cls, raw: Any, registry, export_items, create_classification) -> Optional["EntityTransformers"]:
        spec = _load_json(raw)
        if not spec or not isinstance(spec, list):
            return None
        return cls(spec, registry, export_items, create_classification)

    def apply(self, entity: dict) -> dict:
        if self.handlers:
            handler = entity.get("typeName") if entity.get("typeName") in self.handlers else None
            if handler is None:
                return entity   # with custom handlers only their entity types are transformed (as in Atlas)
        else:
            handler = None
        te = TransformableEntity(entity, handler)
        for conds, acts in self.rules:
            if all(c(te) for c in conds):
                for a in acts:
                    a(te)
        te.complete()
        return entity
