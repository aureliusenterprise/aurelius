"""Atlas DSL (``/v2/search/dsl``) on Elasticsearch.

Implements the Atlas DSL grammar (``AtlasDSLParser.g4``)::

    query      := source+ [groupby (item, ...)] [select item [as label], ...] [orderby expr [asc|desc]]
                  [limit n [offset n]]
    source     := [from] Name [as alias] [where expr] | where expr | expr        (',' may separate sources)
    expr       := comp ((and|or) comp)*          -- left-to-right grouping, like Atlas
    comp       := '(' expr ')' | path op value | path (isa|is) Classification | path has attr
                | path hasTerm term | count() | max(path) | min(path) | sum(path)
    op         := = != < <= > >= like  (also eq neq lt lte gt gte), value may be [v1, v2] (in)

The first source is an entity type, a classification (entities carrying it, incl.
propagated) or ``_CLASSIFIED``/``_NOT_CLASSIFIED``.  Further sources navigate relationship
attributes (``hive_db where name='sales' tables``).  Paths may traverse references
(``hive_table where db.name = 'sales'``), use aliases (``hive_table as t where t.name = 'x'``)
or classification attributes (``hive_table isa PII where PII.level > 1``).

Conditions are translated to Elasticsearch queries; joins over relationships are
resolved by materialising guid sets (capped by ``dsl_max_join``).  select / groupby /
aggregations are computed over the matching documents.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from ..errors import AtlasBaseException, AtlasErrorCode
from ..repository.converter import SYSTEM_ATTR_FIELDS, entity_header
from ..typesystem.registry import ALL_ENTITY_TYPES, TypeRegistry
from .filters import FieldRef, leaf_query

KEYWORDS = {"from", "where", "select", "groupby", "orderby", "limit", "offset", "as", "isa", "is", "has", "hasterm",
            "and", "or", "asc", "desc", "count", "max", "min", "sum", "like", "true", "false"}
WORD_OPS = {"in": "=", "eq": "=", "neq": "!=", "lt": "<", "lte": "<=", "gt": ">", "gte": ">=", "like": "like"}
CLASSIFIED, NOT_CLASSIFIED = "_CLASSIFIED", "_NOT_CLASSIFIED"

_TOKEN = re.compile(r"""
    (?P<ws>\s+|--[^\n]*|/\*.*?\*/)
  | (?P<str>'[^']*'|"[^"]*")
  | (?P<bq>`[^`]*`)
  | (?P<num>[+-]?\d+\.\d+(?:[eE][+-]?\d+)?|[+-]?\d+(?:[eE][+-]?\d+)?)(?![A-Za-z_])
  | (?P<op><=|>=|!=|=|<|>)
  | (?P<punct>[(),\[\].*])
  | (?P<id>[A-Za-z_$][A-Za-z0-9_$]*)
""", re.X | re.S)


@dataclass
class Tok:
    kind: str   # id, str, num, op, punct, kw, eof
    val: Any


def tokenize(q: str) -> List[Tok]:
    out: List[Tok] = []
    pos = 0
    while pos < len(q):
        m = _TOKEN.match(q, pos)
        if not m:
            raise AtlasBaseException(AtlasErrorCode.INVALID_DSL_QUERY, q, f"unexpected character '{q[pos]}' at {pos}")
        pos = m.end()
        k = m.lastgroup
        v = m.group(k)
        if k == "ws":
            continue
        if k == "str":
            out.append(Tok("str", v[1:-1]))
        elif k == "bq":
            out.append(Tok("id", v[1:-1]))
        elif k == "num":
            out.append(Tok("num", float(v) if any(c in v for c in ".eE") else int(v)))
        elif k == "id":
            lv = v.lower()
            out.append(Tok("kw", lv) if lv in KEYWORDS else Tok("id", v))
        else:
            out.append(Tok(k, v))
    out.append(Tok("eof", None))
    return out


# ------------------------------------------------------------------ AST
@dataclass
class Cmp:
    path: List[str]
    op: str
    value: Any


@dataclass
class IsA:
    path: List[str]
    cls: str


@dataclass
class Has:
    path: List[str]
    attr: str


@dataclass
class HasTerm:
    path: List[str]
    term: str


@dataclass
class BoolOp:
    op: str          # AND | OR
    items: list


@dataclass
class Source:
    name: str
    alias: Optional[str] = None
    where: Optional[Any] = None


@dataclass
class SelectItem:
    kind: str                  # attr | count | max | min | sum
    path: Optional[List[str]]
    label: str


@dataclass
class Query:
    sources: List[Source] = field(default_factory=list)
    groupby: List[List[str]] = field(default_factory=list)
    select: List[SelectItem] = field(default_factory=list)
    orderby: Optional[List[str]] = None
    desc: bool = False
    limit: Optional[int] = None
    offset: Optional[int] = None


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.toks = tokenize(text)
        self.i = 0

    def err(self, reason: str):
        raise AtlasBaseException(AtlasErrorCode.INVALID_DSL_QUERY, self.text, reason)

    @property
    def t(self) -> Tok:
        return self.toks[self.i]

    def peek(self, k: int = 1) -> Tok:
        return self.toks[min(self.i + k, len(self.toks) - 1)]

    def is_kw(self, *words) -> bool:
        return self.t.kind == "kw" and self.t.val in words

    def next(self) -> Tok:
        tok = self.t
        self.i += 1
        return tok

    def expect_kw(self, w: str):
        if not self.is_kw(w):
            self.err(f"expected '{w}'")
        self.next()

    def expect_punct(self, p: str):
        if not (self.t.kind == "punct" and self.t.val == p):
            self.err(f"expected '{p}'")
        self.next()

    def ident(self) -> str:
        if self.t.kind in ("id", "str"):
            return str(self.next().val)
        if self.t.kind == "kw" and self.t.val not in ("from", "where", "select", "groupby", "orderby", "limit",
                                                       "offset", "and", "or"):
            return str(self.next().val)
        self.err(f"identifier expected, found {self.t.val!r}")

    def path(self) -> List[str]:
        parts = [self.ident()]
        while self.t.kind == "punct" and self.t.val == ".":
            self.next()
            parts.append(self.ident())
        return parts

    # ---------------------------------------------------------- query
    def parse(self) -> Query:
        q = Query()
        clause_start = ("groupby", "select", "orderby", "limit")
        while self.t.kind != "eof" and not self.is_kw(*clause_start):
            if self.t.kind == "punct" and self.t.val == ",":
                self.next()
                continue
            self.source(q)
        if self.is_kw("groupby"):
            self.next()
            self.expect_punct("(")
            q.groupby.append(self.path())
            while self.t.kind == "punct" and self.t.val == ",":
                self.next()
                q.groupby.append(self.path())
            self.expect_punct(")")
        if self.is_kw("select"):
            self.next()
            q.select.append(self.select_item())
            while self.t.kind == "punct" and self.t.val == ",":
                self.next()
                q.select.append(self.select_item())
        if self.is_kw("orderby"):
            self.next()
            if self.t.kind == "punct" and self.t.val == "(":
                self.next()
                q.orderby = self.path()
                self.expect_punct(")")
            else:
                q.orderby = self.path()
            if self.is_kw("asc", "desc"):
                q.desc = self.next().val == "desc"
        if self.is_kw("limit"):
            self.next()
            if self.t.kind != "num":
                self.err("number expected after limit")
            q.limit = int(self.next().val)
            if self.is_kw("offset"):
                self.next()
                if self.t.kind != "num":
                    self.err("number expected after offset")
                q.offset = int(self.next().val)
        if self.t.kind != "eof":
            self.err(f"unexpected token {self.t.val!r}")
        if not q.sources:
            self.err("a type or classification name is required")
        return q

    def source(self, q: Query) -> None:
        if self.is_kw("from"):
            self.next()
        if self.is_kw("where"):
            if not q.sources:
                self.err("'where' without a source")
            self.next()
            self._add_where(q.sources[-1], self.expr())
            return
        # "Type isa X" / "Type has x" / "Type hasTerm t" / bare conditions continue the current source
        if q.sources and self._starts_condition():
            self._add_where(q.sources[-1], self.expr())
            return
        name = self.ident()
        src = Source(name=name)
        if self.is_kw("as"):
            self.next()
            src.alias = self.ident()
        q.sources.append(src)
        if self.is_kw("isa", "is", "has", "hasterm"):
            self._add_where(src, self.expr(first=self.clause_after([name])))
        if self.is_kw("where"):
            self.next()
            self._add_where(src, self.expr())

    def _starts_condition(self) -> bool:
        t, n = self.t, self.peek()
        if t.kind == "punct" and t.val == "(":
            return True
        if t.kind == "kw" and t.val in ("count", "max", "min", "sum"):
            return True
        if t.kind in ("id", "str") or (t.kind == "kw" and t.val not in KEYWORDS):
            j = 1
            while self.peek(j).kind == "punct" and self.peek(j).val == ".":
                j += 2
            nx = self.peek(j)
            return nx.kind == "op" or (nx.kind == "kw" and nx.val in ("isa", "is", "has", "hasterm", "like")) or \
                (nx.kind == "id" and nx.val.lower() in WORD_OPS)
        return False

    @staticmethod
    def _add_where(src: Source, e) -> None:
        src.where = e if src.where is None else BoolOp("AND", [src.where, e])

    def select_item(self) -> SelectItem:
        start = self.i
        if self.is_kw("count", "max", "min", "sum"):
            fn = self.next().val
            self.expect_punct("(")
            p = None
            if fn != "count":
                p = self.path()
            self.expect_punct(")")
            item = SelectItem(fn, p, "")
        else:
            item = SelectItem("attr", self.path(), "")
        text = "".join(str(t.val) for t in self.toks[start:self.i])
        if self.is_kw("as"):
            self.next()
            item.label = self.ident()
        else:
            item.label = text
        return item

    # ---------------------------------------------------------- expressions
    def expr(self, first=None):
        left = first if first is not None else self.comp()
        result = left
        prev = None
        items = [left]
        while self.is_kw("and", "or"):
            op = self.next().val.upper()
            right = self.comp()
            if prev is None or prev == op:
                items.append(right)
            else:
                items = [BoolOp(prev, items), right]
            prev = op
        if prev is not None:
            result = BoolOp(prev, items)
        return result

    def comp(self):
        if self.t.kind == "punct" and self.t.val == "(":
            self.next()
            e = self.expr()
            self.expect_punct(")")
            return e
        return self.clause_after(self.path())

    def clause_after(self, p: List[str]):
        if self.is_kw("isa", "is"):
            self.next()
            return IsA(p, self.ident())
        if self.is_kw("has"):
            self.next()
            return Has(p, self.ident())
        if self.is_kw("hasterm"):
            self.next()
            return HasTerm(p, self.ident())
        if self.t.kind == "op":
            op = self.next().val
        elif self.is_kw("like"):
            self.next()
            op = "like"
        elif self.t.kind == "id" and self.t.val.lower() in WORD_OPS:
            op = WORD_OPS[self.next().val.lower()]
        else:
            self.err(f"operator expected after {'.'.join(p)}")
        return Cmp(p, op, self.value())

    def value(self):
        t = self.t
        if t.kind == "punct" and t.val == "[":
            self.next()
            vals = [self.value()]
            while self.t.kind == "punct" and self.t.val == ",":
                self.next()
                vals.append(self.value())
            self.expect_punct("]")
            return vals
        if t.kind in ("str", "num", "id"):
            return self.next().val
        if self.is_kw("true", "false"):
            return self.next().val == "true"
        self.err(f"value expected, found {t.val!r}")


# ======================================================================== execution
class DslExecutor:
    def __init__(self, services):
        self.s = services
        self.store = services.store
        self.max_join = getattr(services.settings, "dsl_max_join", 100000)

    @property
    def reg(self) -> TypeRegistry:
        return self.s.typedefs.registry

    def _err(self, q: str, reason: str):
        raise AtlasBaseException(AtlasErrorCode.INVALID_DSL_QUERY, q, reason)

    # ------------------------------------------------------------------ entry
    async def execute(self, query: str, type_name: Optional[str], classification: Optional[str],
                      limit: int, offset: int) -> dict:
        text = query or ""
        if type_name:
            text = f"`{type_name}` {text}"
        if classification and not (query or "").strip():
            text += f" isa `{classification}`"
        self.text = text
        q = Parser(text).parse()
        ctx = await self._resolve_sources(q)
        lim = q.limit if q.limit is not None else limit
        off = q.offset if q.offset is not None else offset
        lim = max(0, min(int(lim if lim is not None else 100), self.s.settings.search_max_limit))
        off = max(0, int(off or 0))
        result: Dict[str, Any] = {"queryType": "DSL", "queryText": query}
        if q.select or q.groupby:
            result["attributes"] = await self._select(q, ctx, lim, off)
            return result
        sort = self._sort(q, ctx)
        r = await self.store.search(self.store.entities, ctx["query"], size=lim, from_=off, sort=sort)
        docs = [h["_source"] for h in r["hits"]["hits"]]
        result["approximateCount"] = r["hits"]["total"]["value"]
        if docs:
            result["entities"] = [entity_header(self.reg, d) for d in docs]
        return result

    # ------------------------------------------------------------------ sources
    async def _resolve_sources(self, q: Query) -> dict:
        reg = self.reg
        first = q.sources[0]
        aliases: Dict[str, str] = {}
        name = first.name
        base: List[dict] = [{"term": {"status": "ACTIVE"}}]
        ctx_type: Optional[str] = None
        ctx_cls: Optional[str] = None
        if name in reg.entities or name == ALL_ENTITY_TYPES:
            if name != ALL_ENTITY_TYPES:
                base.append({"terms": {"typeName": sorted(reg.entities[name].type_and_all_sub_types())}})
                ctx_type = name
        elif name in reg.classifications:
            base.append({"terms": {"allClassificationNames": sorted(reg.classifications[name].type_and_all_sub_types())}})
            ctx_cls = name
        elif name == CLASSIFIED:
            base.append({"exists": {"field": "allClassificationNames"}})
        elif name == NOT_CLASSIFIED:
            base.append({"bool": {"must_not": [{"exists": {"field": "allClassificationNames"}}]}})
        else:
            self._err(self.text, f"{name} is not a valid type or classification")
        if first.alias:
            aliases[first.alias] = ctx_type or name
        scope = {"type": ctx_type, "cls": ctx_cls, "aliases": aliases, "names": {name}}
        if first.where is not None:
            base.append(await self._cond(first.where, scope))
        query = {"bool": {"filter": base}}
        # navigation over relationship attributes
        for src in q.sources[1:]:
            if ctx_type is None:
                self._err(self.text, f"cannot navigate to {src.name} from {name}")
            et = reg.entities[ctx_type]
            ends = et.relationship_attributes.get(src.name)
            if not ends:
                if src.name in reg.entities:
                    # "hive_db hive_table" style: find the relationship attribute leading to that type
                    ends = [e for ends_ in et.relationship_attributes.values() for e in ends_
                            if reg.entities[src.name].isa(e.other_type) or reg.entities[e.other_type].isa(src.name)]
                if not ends:
                    self._err(self.text, f"{src.name} is not an attribute of {ctx_type}")
            guids = await self._guids(query)
            targets = await self._navigate(guids, ends)
            next_type = src.name if src.name in reg.entities else ends[0].other_type
            ctx_type = next_type
            scope = {"type": ctx_type, "cls": None, "aliases": aliases, "names": {src.name, next_type}}
            if src.alias:
                aliases[src.alias] = ctx_type
            filt = [{"term": {"status": "ACTIVE"}}, {"terms": {"guid": sorted(targets) or ["-"]}}]
            if src.name in reg.entities:
                filt.append({"terms": {"typeName": sorted(reg.entities[src.name].type_and_all_sub_types())}})
            if src.where is not None:
                filt.append(await self._cond(src.where, scope))
            query = {"bool": {"filter": filt}}
        return {"query": query, "type": ctx_type, "cls": ctx_cls, "aliases": aliases}

    async def _guids(self, query: dict) -> List[str]:
        out = []
        async for g, _ in self.store.scan(self.store.entities, query, source=["guid"], limit=self.max_join):
            out.append(g)
        return out

    async def _navigate(self, guids: List[str], ends) -> Set[str]:
        out: Set[str] = set()
        for i in range(0, len(guids), 1000):
            chunk = guids[i:i + 1000]
            should = [{"bool": {"filter": [{"term": {"typeName": e.rel.name}}, {"terms": {f"end{e.end}Guid": chunk}}]}}
                      for e in ends]
            q = {"bool": {"filter": [{"term": {"status": "ACTIVE"}}], "should": should, "minimum_should_match": 1}}
            async for _, r in self.store.scan(self.store.relationships, q, limit=self.max_join):
                for e in ends:
                    if r["typeName"] == e.rel.name and r[f"end{e.end}Guid"] in chunk:
                        out.add(r[f"end{e.other_end}Guid"])
        return out

    # ------------------------------------------------------------------ conditions
    def _strip(self, path: List[str], scope: dict) -> List[str]:
        if len(path) > 1 and (path[0] in scope["aliases"] or path[0] in scope["names"] or path[0] == scope.get("type")):
            return path[1:]
        return path

    async def _cond(self, node, scope: dict) -> dict:
        reg = self.reg
        if isinstance(node, BoolOp):
            subs = [await self._cond(n, scope) for n in node.items]
            if node.op == "OR":
                return {"bool": {"should": subs, "minimum_should_match": 1}}
            return {"bool": {"filter": subs}}
        if isinstance(node, IsA):
            c = node.cls
            if c == CLASSIFIED:
                return {"exists": {"field": "allClassificationNames"}}
            if c == NOT_CLASSIFIED:
                return {"bool": {"must_not": [{"exists": {"field": "allClassificationNames"}}]}}
            if c not in reg.classifications:
                self._err(self.text, f"{c} is not a classification")
            return {"terms": {"allClassificationNames": sorted(reg.classifications[c].type_and_all_sub_types())}}
        if isinstance(node, HasTerm):
            t = node.term
            f = "meaningQualifiedNames" if "@" in t else "meaningNames"
            return {"term": {f: t}}
        if isinstance(node, Has):
            return await self._has(node.attr, scope)
        path = self._strip(node.path, scope)
        return await self._cmp(path, node.op, node.value, scope)

    async def _has(self, attr: str, scope: dict) -> dict:
        reg = self.reg
        et = reg.entities.get(scope.get("type") or "")
        if et and attr in et.relationship_attributes and (attr not in et.attributes or et.attributes[attr].is_object_ref):
            ends = et.relationship_attributes[attr]
            owners = set()
            should = [{"term": {"typeName": e.rel.name}} for e in ends]
            q = {"bool": {"filter": [{"term": {"status": "ACTIVE"}}], "should": should, "minimum_should_match": 1}}
            async for _, r in self.store.scan(self.store.relationships, q, limit=self.max_join):
                for e in ends:
                    if r["typeName"] == e.rel.name:
                        owners.add(r[f"end{e.end}Guid"])
            return {"terms": {"guid": sorted(owners) or ["-"]}}
        ref = self._field(attr, scope)
        return {"exists": {"field": ref.field}}

    def _field(self, attr: str, scope: dict) -> FieldRef:
        reg = self.reg
        if attr in SYSTEM_ATTR_FIELDS:
            f, g = SYSTEM_ATTR_FIELDS[attr]
            return FieldRef(f, g, False)
        types = [scope["type"]] if scope.get("type") else []
        if scope.get("type"):
            types += sorted(reg.entities[scope["type"]].all_sub_types)
        for t in types:
            a = reg.entities[t].attributes.get(attr)
            if a is not None:
                if a.index_group is None:
                    self._err(self.text, f"attribute {attr} of {t} cannot be used in a condition")
                return FieldRef(f"idx.{a.index_group}.{attr}", a.index_group, a.index_group == "str", a)
        if not types:
            a = reg.find_attribute_any_type(attr)
            if a is not None:
                return FieldRef(f"idx.{a.index_group}.{attr}", a.index_group, a.index_group == "str", a)
        self._err(self.text, f"{attr} is not a valid attribute of {scope.get('type') or scope.get('cls') or 'entity'}")

    async def _cmp(self, path: List[str], op: str, value: Any, scope: dict) -> dict:
        reg = self.reg
        atlas_op = {"=": "EQ", "!=": "NEQ", "<": "LT", "<=": "LTE", ">": "GT", ">=": "GTE", "like": "LIKE"}[op]
        if isinstance(value, list):
            atlas_op, value = "IN", [str(v) if not isinstance(v, (int, float, bool)) else v for v in value]
        # classification attribute: "PII.level > 1" or, when the source is a classification, "level > 1"
        cls_name, cls_attr = None, None
        if len(path) == 2 and path[0] in reg.classifications:
            cls_name, cls_attr = path
        elif len(path) == 1 and scope.get("cls") and path[0] in reg.classifications[scope["cls"]].attributes:
            cls_name, cls_attr = scope["cls"], path[0]
        if cls_name:
            a = reg.classifications[cls_name].attributes.get(cls_attr)
            if a is None or a.index_group is None:
                self._err(self.text, f"{cls_attr} is not a valid attribute of {cls_name}")
            ref = FieldRef(f"tags.idx.{a.index_group}.{cls_attr}", a.index_group, a.index_group == "str", a)
            inner = leaf_query(ref, atlas_op, value, case_insensitive_eq=False)
            names = sorted(reg.classifications[cls_name].type_and_all_sub_types())
            return {"nested": {"path": "tags", "query": {"bool": {"filter": [{"terms": {"tags.typeName": names}}, inner]}}}}
        if len(path) == 1:
            if path[0] == "name" and not scope.get("type"):
                ref = FieldRef("displayText", "str", True)
            else:
                ref = self._field(path[0], scope)
            if ref.group == "str" and atlas_op == "LIKE":
                value = str(value).replace("%", "*")
            return leaf_query(ref, atlas_op, value, case_insensitive_eq=False)
        # reference traversal: db.name = 'x'
        et = reg.entities.get(scope.get("type") or "")
        if et is None or path[0] not in et.relationship_attributes:
            self._err(self.text, f"{'.'.join(path)} is not a valid attribute path")
        ends = et.relationship_attributes[path[0]]
        target_type = ends[0].other_type
        sub_scope = {"type": target_type, "cls": None, "aliases": {}, "names": set()}
        sub = await self._cmp(path[1:], op, value, sub_scope)
        tq = {"bool": {"filter": [{"term": {"status": "ACTIVE"}},
                                  {"terms": {"typeName": sorted(reg.entities[target_type].type_and_all_sub_types())}}, sub]}}
        targets = await self._guids(tq)
        back = await self._navigate(targets, [_Reverse(e) for e in ends])
        return {"terms": {"guid": sorted(back) or ["-"]}}

    # ------------------------------------------------------------------ sort / select
    def _sort(self, q: Query, ctx: dict) -> list:
        if not q.orderby:
            return [{"displayText.lc": {"order": "asc", "unmapped_type": "keyword", "missing": "_last"}}, {"guid": "asc"}]
        scope = {"type": ctx["type"], "cls": ctx["cls"], "aliases": ctx["aliases"], "names": set()}
        path = self._strip(q.orderby, scope)
        if len(path) != 1:
            self._err(self.text, "orderby supports attributes of the result type only")
        ref = self._field(path[0], scope) if not (path[0] == "name" and not ctx["type"]) else FieldRef("displayText", "str", True)
        field_name = ref.field + (".lc" if ref.has_lc else "")
        return [{field_name: {"order": "desc" if q.desc else "asc", "unmapped_type": "keyword", "missing": "_last"}},
                {"guid": "asc"}]

    async def _values(self, docs: List[dict], path: List[str], scope: dict) -> Dict[str, Any]:
        """Value of an attribute path for each doc (following references)."""
        reg = self.reg
        path = self._strip(path, scope)
        out: Dict[str, Any] = {}
        if len(path) == 1:
            a = path[0]
            for d in docs:
                if a in SYSTEM_ATTR_FIELDS:
                    out[d["guid"]] = d.get(SYSTEM_ATTR_FIELDS[a][0])
                elif a in (d.get("attributes") or {}):
                    out[d["guid"]] = d["attributes"][a]
                else:
                    et = reg.entities.get(d["typeName"])
                    if et and a in et.relationship_attributes:
                        out[d["guid"]] = None  # filled below
                    else:
                        out[d["guid"]] = None
            et = reg.entities.get(scope.get("type") or "")
            if et and a in et.relationship_attributes and (a not in et.attributes or et.attributes[a].is_object_ref):
                refs = await self._related(docs, et.relationship_attributes[a])
                for g, lst in refs.items():
                    heads = [entity_header(reg, x) for x in lst]
                    out[g] = heads[0] if len(heads) == 1 else heads
            return out
        et = reg.entities.get(scope.get("type") or "")
        if et is None or path[0] not in et.relationship_attributes:
            self._err(self.text, f"{'.'.join(path)} is not a valid attribute path")
        ends = et.relationship_attributes[path[0]]
        refs = await self._related(docs, ends)
        all_targets = {x["guid"]: x for lst in refs.values() for x in lst}
        sub = await self._values(list(all_targets.values()), path[1:],
                                 {"type": ends[0].other_type, "cls": None, "aliases": {}, "names": set()})
        for d in docs:
            vals = [sub.get(x["guid"]) for x in refs.get(d["guid"], [])]
            vals = [v for v in vals if v is not None]
            out[d["guid"]] = vals[0] if len(vals) == 1 else (vals or None)
        return out

    async def _related(self, docs: List[dict], ends) -> Dict[str, List[dict]]:
        guids = [d["guid"] for d in docs]
        pairs: List[Tuple[str, str]] = []
        for i in range(0, len(guids), 1000):
            chunk = guids[i:i + 1000]
            should = [{"bool": {"filter": [{"term": {"typeName": e.rel.name}}, {"terms": {f"end{e.end}Guid": chunk}}]}}
                      for e in ends]
            q = {"bool": {"filter": [{"term": {"status": "ACTIVE"}}], "should": should, "minimum_should_match": 1}}
            async for _, r in self.store.scan(self.store.relationships, q, limit=self.max_join):
                for e in ends:
                    if r["typeName"] == e.rel.name and r[f"end{e.end}Guid"] in chunk:
                        pairs.append((r[f"end{e.end}Guid"], r[f"end{e.other_end}Guid"]))
        targets = await self.store.mget(self.store.entities, {t for _, t in pairs})
        out: Dict[str, List[dict]] = {}
        for s, t in pairs:
            if t in targets and targets[t].get("status") == "ACTIVE":
                out.setdefault(s, []).append(targets[t])
        return out

    async def _select(self, q: Query, ctx: dict, limit: int, offset: int) -> dict:
        scope = {"type": ctx["type"], "cls": ctx["cls"], "aliases": ctx["aliases"], "names": set()}
        items = q.select or [SelectItem("attr", p, ".".join(p)) for p in q.groupby]
        labels = [i.label for i in items]
        aggregates = any(i.kind != "attr" for i in items)
        if not q.groupby and not aggregates:
            sort = self._sort(q, ctx)
            r = await self.store.search(self.store.entities, ctx["query"], size=limit, from_=offset, sort=sort)
            docs = [h["_source"] for h in r["hits"]["hits"]]
            cols = [await self._values(docs, i.path, scope) for i in items]
            rows, seen = [], set()
            for d in docs:
                row = [_cell(c.get(d["guid"])) for c in cols]
                key = repr(row)
                if key not in seen:
                    seen.add(key)
                    rows.append(row)
            return {"name": labels, "values": rows}
        docs = [d async for _, d in self.store.scan(self.store.entities, ctx["query"], limit=self.max_join)]
        needed = {tuple(i.path) for i in items if i.path} | {tuple(p) for p in q.groupby}
        colvals = {p: await self._values(docs, list(p), scope) for p in needed}
        groups: Dict[Any, List[dict]] = {}
        if q.groupby:
            for d in docs:
                key = tuple(repr(colvals[tuple(p)].get(d["guid"])) for p in q.groupby)
                groups.setdefault(key, []).append(d)
        else:
            groups[()] = docs
        rows = []
        for members in groups.values():
            row = []
            for it in items:
                vals = [colvals[tuple(it.path)].get(m["guid"]) for m in members] if it.path else []
                vals = [v for v in vals if v is not None and v != ""]
                if it.kind == "count":
                    row.append(len(members))
                elif it.kind == "sum":
                    row.append(float(sum(v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool))))
                elif it.kind in ("max", "min"):
                    if not vals:
                        row.append(None)
                    elif all(isinstance(v, (int, float)) for v in vals):
                        row.append(max(vals) if it.kind == "max" else min(vals))
                    else:
                        sv = [str(v) for v in vals]
                        row.append(max(sv, key=str.lower) if it.kind == "max" else min(sv, key=str.lower))
                else:
                    row.append(_cell(colvals[tuple(it.path)].get(members[0]["guid"])) if members else "")
            rows.append(row)
        if q.orderby:
            ob = ".".join(q.orderby)
            idx = next((k for k, it in enumerate(items) if it.label == ob or (it.path and ".".join(it.path) == ob)), None)
            if idx is None:
                self._err(self.text, f"orderby {ob} must be one of the selected items")
            rows.sort(key=lambda r: _sortkey(r[idx]), reverse=q.desc)
        elif q.groupby:
            rows.sort(key=lambda r: [_sortkey(v) for v in r])
        return {"name": labels, "values": rows[offset:offset + limit]}


class _Reverse:
    """A RelEnd seen from the other side (used to walk a reference back to its owner)."""

    def __init__(self, e):
        self.rel = e.rel
        self.end = e.other_end
        self.other_end = e.end
        self.other_type = e.rel.end(e.end).type


def _cell(v: Any) -> Any:
    return "" if v is None else v


def _sortkey(v: Any):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return (0, v, "")
    return (1, 0, str(v).lower())
