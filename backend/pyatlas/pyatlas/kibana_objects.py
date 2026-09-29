"""Kibana saved objects of Aurelius: data views, Lens visualizations and the dashboards

* "Aurelius activity": logins and changes per day (access log, entity audits; multi-tenant also the Keycloak login
  events of the tenant's realm: failed logins, logins through the customer's identity provider),
* "Aurelius usage": how the frontend is used and how people navigate it (clickstream),
* "Aurelius health" (multi-tenant, from the log data streams): errors, slow requests, lineage API calls, quality
  result uploads.

:func:`saved_objects` builds them for one Kibana space: a single-tenant installation (indices ``<prefix>_*``), one
tenant (``aurelius_<tenant>_*``, ``logs-aurelius.*-<tenant>``) or the operators' platform space (all tenants, with a
``tenant`` field).  ``scripts/gen_kibana_dashboards.py`` writes the single-tenant file
``docker/kibana-dashboards.ndjson``; ``aurelius-admin`` imports the tenant and platform objects.
"""
import json
from typing import List, Optional

LAYER = "layer1"


def col_date(field, label="Day"):
    return {"label": label, "dataType": "date", "operationType": "date_histogram", "sourceField": field,
            "isBucketed": True, "scale": "interval", "params": {"interval": "d", "includeEmptyRows": True}}


def col_terms(field, label, order_by, size=10):
    return {"label": label, "dataType": "string", "operationType": "terms", "sourceField": field, "isBucketed": True,
            "scale": "ordinal", "params": {"size": size, "orderBy": {"type": "column", "columnId": order_by},
                                           "orderDirection": "desc", "otherBucket": True, "missingBucket": False}}


def col_count(label):
    return {"label": label, "dataType": "number", "operationType": "count", "sourceField": "___records___",
            "isBucketed": False, "scale": "ratio", "params": {"emptyAsNull": False}}


def col_unique(field, label):
    return {"label": label, "dataType": "number", "operationType": "unique_count", "sourceField": field,
            "isBucketed": False, "scale": "ratio", "params": {"emptyAsNull": False}}


def lens(obj_id, title, description, data_view, columns, order, visualization, vis_type, query=""):
    state = {
        "datasourceStates": {"formBased": {"layers": {LAYER: {"columns": columns, "columnOrder": order,
                                                               "incompleteColumns": {}, "sampling": 1}}}},
        "visualization": visualization, "query": {"query": query, "language": "kuery"}, "filters": [],
        "internalReferences": [], "adHocDataViews": {}}
    return {"type": "lens", "id": obj_id, "attributes": {"title": title, "description": description,
                                                         "visualizationType": vis_type, "state": state},
            "references": [{"type": "index-pattern", "id": data_view,
                            "name": f"indexpattern-datasource-layer-{LAYER}"}],
            "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.9.0"}


def col_median(field, label):
    return {"label": label, "dataType": "number", "operationType": "median", "sourceField": field,
            "isBucketed": False, "scale": "ratio", "params": {"emptyAsNull": True}}


def xy(series_type, x, y, split=None):
    layer = {"layerId": LAYER, "layerType": "data", "seriesType": series_type, "xAccessor": x,
             "accessors": y if isinstance(y, list) else [y]}
    if split:
        layer["splitAccessor"] = split
    return {"legend": {"isVisible": True, "position": "right"}, "valueLabels": "hide", "fittingFunction": "None",
            "preferredSeriesType": series_type, "layers": [layer]}


def table(*cols):
    return {"layerId": LAYER, "layerType": "data", "columns": [{"columnId": c} for c in cols]}


ACTIVITY = [
    lens("aurelius-logins-per-day", "Logins per day",
         "Keycloak sessions, Atlas UI form logins and Basic (API) users per day", "pyatlas-access",
         {"d": col_date("loginTime"), "m": col_terms("method", "How", "n"), "n": col_count("Logins")},
         ["d", "m", "n"], xy("bar_stacked", "d", "n", "m"), "lnsXY"),
    lens("aurelius-active-users-per-day", "Active users per day", "Distinct users who logged in on the day",
         "pyatlas-access", {"d": col_date("loginTime"), "u": col_unique("user", "Users")}, ["d", "u"],
         xy("bar", "d", "u"), "lnsXY"),
    lens("aurelius-changes-per-day", "Changes per day", "Entity audit events per day and kind of change",
         "pyatlas-audit", {"d": col_date("eventTime"), "a": col_terms("action", "Change", "n"), "n": col_count("Changes")},
         ["d", "a", "n"], xy("bar_stacked", "d", "n", "a"), "lnsXY"),
    lens("aurelius-changes-per-user", "Changes per day by user", "Entity audit events per day and user",
         "pyatlas-audit", {"d": col_date("eventTime"), "u": col_terms("user", "User", "n"), "n": col_count("Changes")},
         ["d", "u", "n"], xy("bar_stacked", "d", "n", "u"), "lnsXY"),
    lens("aurelius-changes-by-user-type", "Changes by user and type", "Who changed which kinds of entities",
         "pyatlas-audit", {"u": col_terms("user", "User", "n", 50), "t": col_terms("typeName", "Entity type", "n", 20),
                           "n": col_count("Changes")}, ["u", "t", "n"], table("u", "t", "n"), "lnsDatatable"),
    lens("aurelius-logins-by-user", "Logins by user", "Logins in the selected period per user", "pyatlas-access",
         {"u": col_terms("user", "User", "n", 50), "n": col_count("Logins"), "k": col_unique("session", "Sessions")},
         ["u", "n", "k"], table("u", "n", "k"), "lnsDatatable"),
]

USAGE = [
    lens("usage-page-views-per-day", "Page views per day", "Navigations in the frontend per day and kind of page",
         "aurelius-clickstream", {"d": col_date("viewTime"), "p": col_terms("page", "Page", "n"), "n": col_count("Page views")},
         ["d", "p", "n"], xy("bar_stacked", "d", "n", "p"), "lnsXY"),
    lens("usage-visits-per-day", "Visits and users per day",
         "A visit is a run of page views of one user without a pause of 30 minutes", "aurelius-clickstream",
         {"d": col_date("viewTime"), "v": col_unique("session", "Visits"), "u": col_unique("user", "Users")},
         ["d", "v", "u"], xy("line", "d", ["v", "u"]), "lnsXY"),
    lens("usage-pages", "Most used pages", "Page views, users and median time spent per kind of page",
         "aurelius-clickstream", {"p": col_terms("page", "Page", "n", 25), "n": col_count("Page views"),
                                  "u": col_unique("user", "Users")}, ["p", "n", "u"], table("p", "n", "u"), "lnsDatatable"),
    lens("usage-navigation", "Where people go next", "Transitions between pages within a visit (from -> to)",
         "aurelius-clickstream", {"f": col_terms("previousPage", "From", "n", 15), "t": col_terms("page", "To", "n", 15),
                                  "n": col_count("Transitions")}, ["f", "t", "n"], table("f", "t", "n"), "lnsDatatable",
         query="previousPage : *"),
    lens("usage-entry-pages", "Where visits start", "First page of each visit", "aurelius-clickstream",
         {"p": col_terms("page", "Page", "n", 10), "n": col_count("Visits")}, ["p", "n"],
         xy("bar_horizontal", "p", "n"), "lnsXY", query="entry : true"),
    lens("usage-time-on-page", "Time on page", "Median seconds before the next page of the visit",
         "aurelius-clickstream", {"p": col_terms("previousPage", "Page", "n", 15), "m": col_median("secondsOnPreviousPage", "Median seconds"),
                                  "n": col_count("Views")}, ["p", "m", "n"], table("p", "m", "n"), "lnsDatatable",
         query="previousPage : *"),
    lens("usage-searches", "What people search for", "Search texts of the search result pages", "aurelius-clickstream",
         {"q": col_terms("query", "Search text", "n", 25), "n": col_count("Searches"), "u": col_unique("user", "Users")},
         ["q", "n", "u"], table("q", "n", "u"), "lnsDatatable", query="query : *"),
    lens("usage-entity-types", "Viewed entity types", "Details and edit pages per entity type", "aurelius-clickstream",
         {"t": col_terms("entityType", "Entity type", "n", 15), "n": col_count("Views")}, ["t", "n"],
         xy("bar_horizontal", "t", "n"), "lnsXY", query="entityType : *"),
    lens("usage-entities", "Most viewed entities", "Entities whose details or edit pages were opened most",
         "aurelius-clickstream", {"e": col_terms("entityName", "Entity", "n", 25), "t": col_terms("entityType", "Type", "n", 3),
                                  "n": col_count("Views"), "u": col_unique("user", "Users")}, ["e", "t", "n", "u"],
         table("e", "t", "n", "u"), "lnsDatatable", query="entityName : *"),
    lens("usage-users", "Usage per user", "Visits and page views per user", "aurelius-clickstream",
         {"u": col_terms("user", "User", "n", 50), "v": col_unique("session", "Visits"), "n": col_count("Page views")},
         ["u", "v", "n"], table("u", "v", "n"), "lnsDatatable"),
]


def dashboard(obj_id, title, description, layout):
    panels, refs = [], []
    for i, (vis_id, x, y, w, h) in enumerate(layout, 1):
        p = f"p{i}"
        panels.append({"type": "lens", "gridData": {"x": x, "y": y, "w": w, "h": h, "i": p}, "panelIndex": p,
                       "embeddableConfig": {"enhancements": {}}, "panelRefName": f"panel_{p}"})
        refs.append({"name": f"{p}:panel_{p}", "type": "lens", "id": vis_id})
    return {"type": "dashboard", "id": obj_id,
            "attributes": {"title": title, "description": description, "timeRestore": True, "timeFrom": "now-30d",
                           "timeTo": "now", "refreshInterval": {"pause": True, "value": 60000},
                           "panelsJSON": json.dumps(panels),
                           "optionsJSON": json.dumps({"useMargins": True, "syncColors": False, "syncCursor": True,
                                                      "syncTooltips": False, "hidePanelTitles": False}),
                           "kibanaSavedObjectMeta": {"searchSourceJSON": json.dumps(
                               {"query": {"query": "", "language": "kuery"}, "filter": []})}},
            "references": refs, "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.9.0"}




def dashboard(obj_id, title, description, layout):
    panels, refs = [], []
    for i, (vis_id, x, y, w, h) in enumerate(layout, 1):
        p = f"p{i}"
        panels.append({"type": "lens", "gridData": {"x": x, "y": y, "w": w, "h": h, "i": p}, "panelIndex": p,
                       "embeddableConfig": {"enhancements": {}}, "panelRefName": f"panel_{p}"})
        refs.append({"name": f"{p}:panel_{p}", "type": "lens", "id": vis_id})
    return {"type": "dashboard", "id": obj_id,
            "attributes": {"title": title, "description": description, "timeRestore": True, "timeFrom": "now-30d",
                           "timeTo": "now", "refreshInterval": {"pause": True, "value": 60000},
                           "panelsJSON": json.dumps(panels),
                           "optionsJSON": json.dumps({"useMargins": True, "syncColors": False, "syncCursor": True,
                                                      "syncTooltips": False, "hidePanelTitles": False}),
                           "kibanaSavedObjectMeta": {"searchSourceJSON": json.dumps(
                               {"query": {"query": "", "language": "kuery"}, "filter": []})}},
            "references": refs, "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.9.0"}


# ---- multi-tenant additions: Keycloak login events and the log data streams --------------------------------------
KEYCLOAK = [
    lens("keycloak-logins-per-day", "Keycloak logins and failed logins per day",
         "Login events of the organisation's realm (LOGIN, LOGIN_ERROR, ...)", "logs-keycloak",
         {"d": col_date("@timestamp"), "t": col_terms("kc.type", "Event", "n"), "n": col_count("Events")},
         ["d", "t", "n"], xy("bar_stacked", "d", "n", "t"), "lnsXY", query="kc.type : LOGIN*"),
    lens("keycloak-failed-logins", "Failed logins", "Failed logins by user name and reason", "logs-keycloak",
         {"u": col_terms("kc.username", "User name", "n", 25), "e": col_terms("kc.error", "Reason", "n", 5),
          "n": col_count("Failed logins")}, ["u", "e", "n"], table("u", "e", "n"), "lnsDatatable",
         query="kc.type : LOGIN_ERROR"),
    lens("keycloak-identity-providers", "Logins by identity provider",
         "Logins through the organisation's identity provider (e.g. Entra ID) versus local accounts", "logs-keycloak",
         {"p": col_terms("kc.identity_provider", "Identity provider", "n", 10), "n": col_count("Logins")},
         ["p", "n"], xy("bar_horizontal", "p", "n"), "lnsXY", query="kc.type : LOGIN"),
]

HEALTH = [
    lens("health-requests-per-day", "API requests per day", "Requests to pyatlas per day and status",
         "logs-pyatlas", {"d": col_date("@timestamp"), "s": col_terms("status", "Status", "n", 8),
                          "n": col_count("Requests")}, ["d", "s", "n"], xy("bar_stacked", "d", "n", "s"), "lnsXY",
         query='log.logger : "pyatlas.request"'),
    lens("health-errors-per-day", "Errors and warnings per day", "Log lines of level error and warning",
         "logs-pyatlas", {"d": col_date("@timestamp"), "l": col_terms("log.level", "Level", "n", 3),
                          "n": col_count("Lines")}, ["d", "l", "n"], xy("bar_stacked", "d", "n", "l"), "lnsXY",
         query="log.level : (error or warning)"),
    lens("health-slow-requests", "Slowest API calls", "Median duration per path (ms)", "logs-pyatlas",
         {"p": col_terms("path", "Path", "m", 20), "m": col_median("duration_ms", "Median ms"),
          "n": col_count("Requests")}, ["p", "m", "n"], table("p", "m", "n"), "lnsDatatable",
         query='log.logger : "pyatlas.request"'),
    lens("health-lineage-api", "Lineage API calls", "Calls of the lineage registration API per endpoint and status",
         "logs-pyatlas", {"p": col_terms("path", "Endpoint", "n", 30), "s": col_terms("status", "Status", "n", 5),
                          "n": col_count("Calls")}, ["p", "s", "n"], table("p", "s", "n"), "lnsDatatable",
         query='log.logger : "pyatlas.request" and path : /api/lin_api/*'),
    lens("health-quality-uploads", "Quality result uploads", "Uploads of data quality results per day",
         "logs-pyatlas", {"d": col_date("@timestamp"), "s": col_terms("status", "Status", "n", 5),
                          "n": col_count("Uploads")}, ["d", "s", "n"], xy("bar_stacked", "d", "n", "s"), "lnsXY",
         query='log.logger : "pyatlas.request" and path : "/api/aurelius/quality/results"'),
    lens("health-proxy-status", "Requests at the proxy", "All requests of the organisation's addresses per status",
         "logs-proxy", {"d": col_date("@timestamp"), "s": col_terms("status", "Status", "n", 8),
                        "n": col_count("Requests")}, ["d", "s", "n"], xy("bar_stacked", "d", "n", "s"), "lnsXY"),
]


def _runtime_date(name: str, field: str) -> dict:
    return {name: {"type": "date", "script": {"source": f'if (doc.containsKey("{field}") && doc["{field}"].size() > 0) '
                                                         f'emit(doc["{field}"].value);'}}}


TENANT_FROM_INDEX = {"tenant": {"type": "keyword", "script": {"source": (
    "def i = doc['_index'].value; def m = /^(?:\\.ds-)?(?:aurelius_([a-z0-9-]+)_|logs-aurelius\\.[a-z]+-([a-z0-9-]+)-)/"
    ".matcher(i); if (m.find()) { emit(m.group(1) != null ? m.group(1) : m.group(2)); }")}}}


def data_view(view_id: str, pattern: str, name: str, time_field: Optional[str] = None,
              runtime: Optional[dict] = None) -> dict:
    attrs = {"title": pattern, "name": name, "allowNoIndex": True, "runtimeFieldMap": json.dumps(runtime or {})}
    if time_field:
        attrs["timeFieldName"] = time_field
    return {"type": "index-pattern", "id": view_id, "attributes": attrs, "references": [],
            "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.0.0"}


def data_views(index_pattern: str, logs_namespace: Optional[str], platform: bool = False) -> List[dict]:
    """``index_pattern`` names indices, e.g. ``aurelius_acme`` or ``aurelius_*``; ``logs_namespace`` the log data
    streams' namespace (tenant, ``*`` for the platform), None = no log data streams (single tenant)."""
    p = index_pattern
    extra = TENANT_FROM_INDEX if platform else {}

    def rt(name, field):
        return {**_runtime_date(name, field), **extra}
    out = [
        data_view("pyatlas-entities", f"{p}_entities", "Atlas entities", "updated",
                  {**rt("updated", "updateTime"), **_runtime_date("created", "createTime")}),
        data_view("pyatlas-relationships", f"{p}_relationships", "Atlas relationships", "updated",
                  rt("updated", "updateTime")),
        data_view("pyatlas-audit", f"{p}_audit", "Atlas entity audits", "eventTime", rt("eventTime", "timestamp")),
        data_view("pyatlas-access", f"{p}_access", "Logins (access log)", "loginTime", rt("loginTime", "timestamp")),
        data_view("aurelius-clickstream", f"{p}_clickstream", "Aurelius clickstream (page views)", "viewTime",
                  rt("viewTime", "timestamp")),
        data_view("aurelius-search", f"{p}_aurelius_atlas_dev", "Aurelius search documents", None, extra),
        data_view("aurelius-quality", f"{p}_aurelius_atlas_dev_quality", "Aurelius data quality", None, extra),
        data_view("aurelius-gov-quality", f"{p}_aurelius_atlas_dev_gov_quality", "Aurelius governance quality",
                  None, extra),
    ]
    if logs_namespace is not None:
        ns = logs_namespace
        out += [
            data_view("logs-pyatlas", f"logs-aurelius.pyatlas-{ns}", "Logs: pyatlas", "@timestamp", extra),
            data_view("logs-proxy", f"logs-aurelius.proxy-{ns}", "Logs: reverse proxy", "@timestamp", extra),
            data_view("logs-keycloak", f"logs-aurelius.keycloak-{ns}", "Logs: Keycloak login events", "@timestamp",
                      extra),
        ]
    return out


def dashboards(multi_tenant: bool) -> List[dict]:
    act_layout = [("aurelius-logins-per-day", 0, 0, 24, 14), ("aurelius-active-users-per-day", 24, 0, 24, 14),
                  ("aurelius-changes-per-day", 0, 14, 24, 14), ("aurelius-changes-per-user", 24, 14, 24, 14),
                  ("aurelius-changes-by-user-type", 0, 28, 24, 16), ("aurelius-logins-by-user", 24, 28, 24, 16)]
    if multi_tenant:
        act_layout += [("keycloak-logins-per-day", 0, 44, 24, 14), ("keycloak-identity-providers", 24, 44, 24, 14),
                       ("keycloak-failed-logins", 0, 58, 48, 14)]
    out = [dashboard("aurelius-activity", "Aurelius activity",
                     "Logins and changes per day (access log, entity audits" +
                     (", Keycloak login events)" if multi_tenant else ")"), act_layout),
           dashboard("aurelius-usage", "Aurelius usage",
                     "How the Aurelius frontend is used and how people navigate it (clickstream)",
                     [("usage-page-views-per-day", 0, 0, 24, 14), ("usage-visits-per-day", 24, 0, 24, 14),
                      ("usage-pages", 0, 14, 16, 15), ("usage-navigation", 16, 14, 16, 15),
                      ("usage-entry-pages", 32, 14, 16, 15), ("usage-time-on-page", 0, 29, 16, 15),
                      ("usage-searches", 16, 29, 16, 15), ("usage-entity-types", 32, 29, 16, 15),
                      ("usage-entities", 0, 44, 24, 16), ("usage-users", 24, 44, 24, 16)])]
    if multi_tenant:
        out.append(dashboard("aurelius-health", "Aurelius health",
                             "Errors, slow requests, lineage API calls and quality uploads (log data streams)",
                             [("health-requests-per-day", 0, 0, 24, 14), ("health-errors-per-day", 24, 0, 24, 14),
                              ("health-slow-requests", 0, 14, 24, 16), ("health-lineage-api", 24, 14, 24, 16),
                              ("health-quality-uploads", 0, 30, 24, 14), ("health-proxy-status", 24, 30, 24, 14)]))
    return out


def saved_objects(index_pattern: str, logs_namespace: Optional[str] = None, platform: bool = False) -> List[dict]:
    multi = logs_namespace is not None
    lenses = ACTIVITY + USAGE + (KEYCLOAK + HEALTH if multi else [])
    return [*data_views(index_pattern, logs_namespace, platform), *lenses, *dashboards(multi)]


def ndjson(objects: List[dict]) -> str:
    return "".join(json.dumps(o) + "\n" for o in objects)
