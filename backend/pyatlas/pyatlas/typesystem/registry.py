"""In-memory, fully resolved view of the Atlas type system.

A :class:`TypeRegistry` is built from the raw typedef dictionaries (exactly the
JSON Atlas uses) and resolves super types, inherited attributes, relationship
attributes and unique attributes.  Building a registry validates the whole set of
definitions, so the typedef store validates a change by building a candidate
registry before persisting anything.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode

ENUM, STRUCT, CLASSIFICATION, ENTITY, RELATIONSHIP, BUSINESS_METADATA = (
    "ENUM", "STRUCT", "CLASSIFICATION", "ENTITY", "RELATIONSHIP", "BUSINESS_METADATA")

CATEGORY_LIST_KEYS = {
    ENUM: "enumDefs",
    STRUCT: "structDefs",
    CLASSIFICATION: "classificationDefs",
    ENTITY: "entityDefs",
    RELATIONSHIP: "relationshipDefs",
    BUSINESS_METADATA: "businessMetadataDefs",
}
LIST_KEY_CATEGORIES = {v: k for k, v in CATEGORY_LIST_KEYS.items()}

INTEGRAL = {"byte", "short", "int", "long", "biginteger"}
FRACTIONAL = {"float", "double", "bigdecimal"}
PRIMITIVES = INTEGRAL | FRACTIONAL | {"boolean", "string", "date"}
OBJECT_ID_TYPE = "objectid"

ALL_ENTITY_TYPES = "_ALL_ENTITY_TYPES"
ALL_CLASSIFICATION_TYPES = "_ALL_CLASSIFICATION_TYPES"

SINGLE, SET, LIST = "SINGLE", "SET", "LIST"

_ARRAY_RE = re.compile(r"^array<(.+)>$")
_MAP_RE = re.compile(r"^map<([^,]+),(.+)>$")


def parse_type(type_str: str) -> Tuple[str, Any]:
    """Return ("array", elem) | ("map", (k, v)) | ("simple", name)."""
    t = type_str.strip()
    m = _ARRAY_RE.match(t)
    if m:
        return "array", m.group(1).strip()
    m = _MAP_RE.match(t)
    if m:
        return "map", (m.group(1).strip(), m.group(2).strip())
    return "simple", t


def base_type_name(type_str: str) -> str:
    kind, arg = parse_type(type_str)
    if kind == "array":
        return base_type_name(arg)
    if kind == "map":
        return base_type_name(arg[1])
    return arg


def index_group_for(prim: str) -> Optional[str]:
    if prim == "string":
        return "str"
    if prim in INTEGRAL or prim == "date":
        return "lng"
    if prim in FRACTIONAL:
        return "dbl"
    if prim == "boolean":
        return "bool"
    return None


@dataclass
class AttributeInfo:
    name: str
    type_name: str
    adef: dict
    declaring_type: str
    is_optional: bool = True
    cardinality: str = SINGLE
    is_unique: bool = False
    is_indexable: bool = False
    search_weight: int = -1
    owned_ref: bool = False
    # derived
    kind: str = "simple"            # simple|array|map
    base: str = "string"           # base element type name
    base_category: str = "PRIMITIVE"  # PRIMITIVE|ENUM|STRUCT|ENTITY|OBJECTID|CLASSIFICATION
    index_group: Optional[str] = None
    is_object_ref: bool = False     # value(s) reference entities
    legacy_rel: bool = False        # handled through a relationshipDef with isLegacyAttribute
    is_soft_ref: bool = False       # options.isSoftReference: stored as object ids, no relationship

    @property
    def default_value(self) -> Any:
        return self.adef.get("defaultValue")


@dataclass
class EndDef:
    type: str
    name: str
    is_container: bool
    cardinality: str
    is_legacy: bool
    description: Optional[str] = None


@dataclass
class RelationshipType:
    name: str
    rdef: dict
    category: str
    propagate_tags: str
    label: str
    end1: EndDef
    end2: EndDef
    synthetic: bool = False
    attribute_defs: Dict[str, AttributeInfo] = field(default_factory=dict)

    def end(self, n: int) -> EndDef:
        return self.end1 if n == 1 else self.end2


@dataclass
class RelEnd:
    """Relationship attribute ``attr_name`` of an entity type that sits at end ``end`` of ``rel``."""
    rel: RelationshipType
    end: int
    attr_name: str
    cardinality: str
    is_container: bool
    is_legacy: bool

    @property
    def other_end(self) -> int:
        return 2 if self.end == 1 else 1

    @property
    def other_type(self) -> str:
        return self.rel.end(self.other_end).type

    @property
    def other_cardinality(self) -> str:
        return self.rel.end(self.other_end).cardinality

    @property
    def owns_other(self) -> bool:
        """True if deleting this side must cascade to the other side (composition container)."""
        return self.rel.category == "COMPOSITION" and self.is_container


@dataclass
class StructLikeType:
    name: str
    category: str
    tdef: dict
    super_types: List[str] = field(default_factory=list)
    all_super_types: Set[str] = field(default_factory=set)
    sub_types: Set[str] = field(default_factory=set)
    all_sub_types: Set[str] = field(default_factory=set)
    attributes: Dict[str, AttributeInfo] = field(default_factory=dict)
    # entity only
    relationship_attributes: Dict[str, List[RelEnd]] = field(default_factory=dict)
    unique_attributes: List[str] = field(default_factory=list)
    # classification only
    entity_types: Optional[Set[str]] = None  # resolved allowed entity types (None = any)

    def type_and_all_sub_types(self) -> Set[str]:
        return {self.name} | self.all_sub_types

    def type_and_all_super_types(self) -> Set[str]:
        return {self.name} | self.all_super_types

    def isa(self, other: str) -> bool:
        return other == self.name or other in self.all_super_types

    @property
    def options(self) -> dict:
        return self.tdef.get("options") or {}


@dataclass
class EnumType:
    name: str
    tdef: dict
    values: List[str]
    ordinals: Dict[int, str]
    default: Optional[str]


@dataclass
class BusinessMetadataType:
    name: str
    tdef: dict
    attributes: Dict[str, AttributeInfo]
    applicable: Dict[str, Optional[Set[str]]]   # attr -> allowed entity types (incl. subtypes); None=any
    max_len: Dict[str, Optional[int]]


class TypeRegistry:
    def __init__(self, defs: Dict[str, dict]):
        self.defs: Dict[str, dict] = defs
        self.enums: Dict[str, EnumType] = {}
        self.structs: Dict[str, StructLikeType] = {}
        self.classifications: Dict[str, StructLikeType] = {}
        self.entities: Dict[str, StructLikeType] = {}
        self.relationships: Dict[str, RelationshipType] = {}
        self.business_metadata: Dict[str, BusinessMetadataType] = {}
        self.by_guid: Dict[str, str] = {}
        self.search_weights: Dict[str, int] = {}
        self.internal_types: List[str] = []
        self._build()

    # ------------------------------------------------------------------ lookup
    def category_of(self, name: str) -> Optional[str]:
        d = self.defs.get(name)
        return d.get("category") if d else None

    def get_def(self, name: str) -> Optional[dict]:
        return self.defs.get(name)

    def entity_type(self, name: str) -> StructLikeType:
        t = self.entities.get(name)
        if t is None:
            raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, name)
        return t

    def classification_type(self, name: str) -> StructLikeType:
        t = self.classifications.get(name)
        if t is None:
            raise AtlasBaseException(AtlasErrorCode.CLASSIFICATION_NOT_FOUND, name)
        return t

    def struct_like(self, name: str) -> Optional[StructLikeType]:
        return self.entities.get(name) or self.structs.get(name) or self.classifications.get(name)

    def relationship_type(self, name: str) -> RelationshipType:
        t = self.relationships.get(name)
        if t is None:
            raise AtlasBaseException(AtlasErrorCode.TYPE_NAME_NOT_FOUND, name)
        return t

    def find_attribute_any_type(self, attr: str) -> Optional[AttributeInfo]:
        for t in self.entities.values():
            a = t.attributes.get(attr)
            if a is not None and a.index_group:
                return a
        return None

    # ------------------------------------------------------------------ build
    def _fail(self, msg: str):
        raise AtlasBaseException(AtlasErrorCode.INVALID_TYPE_DEFINITION, msg)

    def _build(self) -> None:
        for name, d in self.defs.items():
            cat = d.get("category")
            if cat not in CATEGORY_LIST_KEYS:
                self._fail(f"{name}: unknown category {cat}")
            if d.get("guid"):
                self.by_guid[d["guid"]] = name
            if cat == ENUM:
                elems = d.get("elementDefs") or []
                values = [e["value"] for e in elems]
                ordinals = {int(e.get("ordinal", i)): e["value"] for i, e in enumerate(elems)}
                self.enums[name] = EnumType(name, d, values, ordinals, d.get("defaultValue"))
            elif cat in (STRUCT, CLASSIFICATION, ENTITY):
                t = StructLikeType(name, cat, d, super_types=list(d.get("superTypes") or []))
                {STRUCT: self.structs, CLASSIFICATION: self.classifications, ENTITY: self.entities}[cat][name] = t

        # super type closure
        for group in (self.classifications, self.entities):
            for t in group.values():
                for st in t.super_types:
                    if st not in group:
                        self._fail(f"{t.name}: unknown super type {st}")
            for t in group.values():
                t.all_super_types = self._closure(group, t.name, set())
                for st in t.super_types:
                    group[st].sub_types.add(t.name)
            for t in group.values():
                for st in t.all_super_types:
                    group[st].all_sub_types.add(t.name)

        # attributes (after closure so we can inherit in topological order)
        for group in (self.structs, self.classifications, self.entities):
            for t in group.values():
                self._resolve_attributes(t, group)

        for name, d in self.defs.items():
            cat = d.get("category")
            if cat == RELATIONSHIP:
                self._add_relationship(name, d)
            elif cat == BUSINESS_METADATA:
                self._add_business_metadata(name, d)

        self._add_synthetic_relationships()

        self.internal_types = sorted(n for n, t in self.entities.items()
                                     if n.startswith("__") or "__internal" in t.all_super_types)
        for t in self.entities.values():
            t.unique_attributes = [a.name for a in t.attributes.values() if a.is_unique]
            for a in t.attributes.values():
                if a.search_weight and a.search_weight > 0 and a.index_group == "str":
                    self.search_weights[a.name] = max(self.search_weights.get(a.name, 0), a.search_weight)

        for t in self.classifications.values():
            restrict: Set[str] = set()
            has_restrictions = False
            for cname in t.type_and_all_super_types():
                ets = self.classifications[cname].tdef.get("entityTypes") or []
                for et in ets:
                    has_restrictions = True
                    if et in self.entities:
                        restrict |= self.entities[et].type_and_all_sub_types()
            t.entity_types = restrict if has_restrictions else None

    def _closure(self, group, name: str, visiting: Set[str]) -> Set[str]:
        if name in visiting:
            self._fail(f"{name}: cyclic super type hierarchy")
        visiting = visiting | {name}
        out: Set[str] = set()
        for st in group[name].super_types:
            out.add(st)
            out |= self._closure(group, st, visiting)
        return out

    def _resolve_attributes(self, t: StructLikeType, group) -> None:
        if t.attributes:
            return
        attrs: Dict[str, AttributeInfo] = {}
        for st in t.super_types:
            sup = group[st]
            self._resolve_attributes(sup, group)
            for k, v in sup.attributes.items():
                attrs.setdefault(k, v)
        for adef in t.tdef.get("attributeDefs") or []:
            info = self._attribute_info(t.name, adef)
            attrs[info.name] = info
        t.attributes = attrs

    def _attribute_info(self, declaring: str, adef: dict) -> AttributeInfo:
        name = adef.get("name")
        type_name = adef.get("typeName")
        if not name or not type_name:
            self._fail(f"{declaring}: attribute without name/typeName")
        kind, _ = parse_type(type_name)
        base = base_type_name(type_name)
        if base in PRIMITIVES:
            base_cat = "PRIMITIVE"
        elif base == OBJECT_ID_TYPE:
            base_cat = "OBJECTID"
        else:
            base_cat = self.category_of(base)
            if base_cat is None:
                self._fail(f"{declaring}.{name}: unknown type {type_name}")
        card = adef.get("cardinality") or SINGLE
        if card in (SET, LIST) and kind != "array":
            raise AtlasBaseException(AtlasErrorCode.INVALID_ATTRIBUTE_TYPE_FOR_CARDINALITY, declaring, name)
        group = None
        if base_cat == "PRIMITIVE" and kind != "map":
            group = index_group_for(base)
        elif base_cat == ENUM and kind != "map":
            group = "str"
        constraints = adef.get("constraints") or []
        owned = any(c.get("type") == "ownedRef" for c in constraints)
        soft = base_cat in (ENTITY, "OBJECTID") and \
            str((adef.get("options") or {}).get("isSoftReference", "")).lower() == "true"
        return AttributeInfo(
            name=name, type_name=type_name, adef=adef, declaring_type=declaring,
            is_optional=bool(adef.get("isOptional", True)), cardinality=card,
            is_unique=bool(adef.get("isUnique", False)), is_indexable=bool(adef.get("isIndexable", False)),
            search_weight=int(adef.get("searchWeight", -1) or -1), owned_ref=owned,
            kind=kind, base=base, base_category=base_cat, index_group=group,
            is_object_ref=base_cat in (ENTITY, "OBJECTID") and not soft, is_soft_ref=soft,
        )

    def _add_relationship(self, name: str, d: dict) -> None:
        ends = []
        for key in ("endDef1", "endDef2"):
            e = d.get(key)
            if not e or not e.get("type"):
                raise AtlasBaseException(AtlasErrorCode.RELATIONSHIP_END_IS_NULL, key)
            if e["type"] not in self.entities:
                self._fail(f"{name}: {key} type {e['type']} is not an entity type")
            ends.append(EndDef(type=e["type"], name=e.get("name") or "", is_container=bool(e.get("isContainer", False)),
                               cardinality=e.get("cardinality") or SINGLE, is_legacy=bool(e.get("isLegacyAttribute", False)),
                               description=e.get("description")))
        category = d.get("relationshipCategory") or "ASSOCIATION"
        if category not in ("ASSOCIATION", "AGGREGATION", "COMPOSITION"):
            self._fail(f"{name}: invalid relationshipCategory {category}")
        if category == "ASSOCIATION" and (ends[0].is_container or ends[1].is_container):
            raise AtlasBaseException(AtlasErrorCode.RELATIONSHIPDEF_INVALID, f"{name}: ASSOCIATION cannot have a container end")
        label = d.get("relationshipLabel") or f"__{ends[0].type}.{ends[0].name}"
        rt = RelationshipType(name=name, rdef=d, category=category, propagate_tags=d.get("propagateTags") or "NONE",
                              label=label, end1=ends[0], end2=ends[1])
        for adef in d.get("attributeDefs") or []:
            info = self._attribute_info(name, adef)
            rt.attribute_defs[info.name] = info
        self.relationships[name] = rt
        for n, e in ((1, ends[0]), (2, ends[1])):
            if not e.name:
                continue
            et = self.entities[e.type]
            for tname in et.type_and_all_sub_types():
                self.entities[tname].relationship_attributes.setdefault(e.name, []).append(
                    RelEnd(rel=rt, end=n, attr_name=e.name, cardinality=e.cardinality,
                           is_container=e.is_container, is_legacy=e.is_legacy))
                a = self.entities[tname].attributes.get(e.name)
                if a is not None and e.is_legacy:
                    a.legacy_rel = True

    def _add_synthetic_relationships(self) -> None:
        """Entity-typed attributes that are not backed by a relationshipDef become implicit relationships."""
        for t in self.entities.values():
            for a in t.attributes.values():
                if not a.is_object_ref or a.legacy_rel or a.declaring_type != t.name:
                    continue
                if a.base_category == "OBJECTID":
                    target = "Referenceable" if "Referenceable" in self.entities else t.name
                else:
                    target = a.base
                rname = f"__{t.name}.{a.name}"
                if rname in self.relationships:
                    continue
                card = SINGLE if a.kind == "simple" else (a.cardinality if a.cardinality != SINGLE else SET)
                rt = RelationshipType(
                    name=rname, rdef={}, category="COMPOSITION" if a.owned_ref else "ASSOCIATION",
                    propagate_tags="NONE", label=rname,
                    end1=EndDef(type=t.name, name=a.name, is_container=a.owned_ref, cardinality=card, is_legacy=True),
                    end2=EndDef(type=target, name="", is_container=False, cardinality=SET, is_legacy=False),
                    synthetic=True)
                self.relationships[rname] = rt
                for tname in t.type_and_all_sub_types():
                    self.entities[tname].relationship_attributes.setdefault(a.name, []).append(
                        RelEnd(rel=rt, end=1, attr_name=a.name, cardinality=card, is_container=a.owned_ref, is_legacy=True))
                a.legacy_rel = True

    def _add_business_metadata(self, name: str, d: dict) -> None:
        attrs: Dict[str, AttributeInfo] = {}
        applicable: Dict[str, Optional[Set[str]]] = {}
        max_len: Dict[str, Optional[int]] = {}
        for adef in d.get("attributeDefs") or []:
            info = self._attribute_info(name, adef)
            if info.is_object_ref:
                self._fail(f"{name}.{info.name}: business metadata attributes cannot reference entities")
            attrs[info.name] = info
            opts = adef.get("options") or {}
            raw = opts.get("applicableEntityTypes")
            types: Optional[Set[str]] = None
            if raw:
                try:
                    lst = json.loads(raw) if isinstance(raw, str) else list(raw)
                except ValueError:
                    lst = [raw]
                types = set()
                for et in lst:
                    if et not in self.entities:
                        self._fail(f"{name}.{info.name}: unknown applicable entity type {et}")
                    types |= self.entities[et].type_and_all_sub_types()
            applicable[info.name] = types
            ml = opts.get("maxStrLength")
            max_len[info.name] = int(ml) if ml not in (None, "") else None
        self.business_metadata[name] = BusinessMetadataType(name, d, attrs, applicable, max_len)

    # ------------------------------------------------------------------ helpers for API output
    def api_def(self, name: str) -> dict:
        """Typedef as returned by the REST API, including computed fields."""
        d = dict(self.defs[name])
        cat = d.get("category")
        if cat == ENTITY:
            t = self.entities[name]
            d["subTypes"] = sorted(t.sub_types)
            d["relationshipAttributeDefs"] = self._relationship_attribute_defs(t)
            bad = self._business_attribute_defs(t)
            if bad:
                d["businessAttributeDefs"] = bad
        elif cat == CLASSIFICATION:
            d["subTypes"] = sorted(self.classifications[name].sub_types)
        d.setdefault("attributeDefs", []) if cat in (STRUCT, CLASSIFICATION, ENTITY, RELATIONSHIP, BUSINESS_METADATA) else None
        if cat in (ENTITY, CLASSIFICATION):
            d.setdefault("superTypes", [])
        return d

    def _relationship_attribute_defs(self, t: StructLikeType) -> List[dict]:
        out = []
        for attr, ends in sorted(t.relationship_attributes.items()):
            for re_ in ends:
                if re_.rel.synthetic:
                    continue
                other = re_.other_type
                tname = other if re_.cardinality == SINGLE else f"array<{other}>"
                out.append({
                    "name": attr, "typeName": tname, "isOptional": True, "cardinality": re_.cardinality,
                    "valuesMinCount": -1, "valuesMaxCount": -1, "isUnique": False, "isIndexable": False,
                    "includeInNotification": False, "searchWeight": -1,
                    "constraints": [{"type": "ownedRef"}] if re_.owns_other else [],
                    "relationshipTypeName": re_.rel.name, "isLegacyAttribute": re_.is_legacy,
                })
        return out

    def _business_attribute_defs(self, t: StructLikeType) -> Dict[str, List[dict]]:
        out: Dict[str, List[dict]] = {}
        for bm in self.business_metadata.values():
            lst = [a.adef for an, a in bm.attributes.items()
                   if bm.applicable.get(an) is None or t.name in bm.applicable[an]]
            if lst:
                out[bm.name] = lst
        return out

    def display_text_attribute(self, type_name: str) -> Optional[str]:
        t = self.entities.get(type_name)
        if t is None:
            return None
        return t.options.get("displayTextAttribute")

    def types_with_supertypes(self, names: Iterable[str]) -> Set[str]:
        out: Set[str] = set()
        for n in names:
            t = self.entities.get(n)
            if t:
                out |= t.type_and_all_sub_types()
        return out
