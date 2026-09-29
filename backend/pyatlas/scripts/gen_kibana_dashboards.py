"""Writes ``docker/kibana-dashboards.ndjson`` with the Kibana dashboards and their Lens visualizations, imported by
``docker/kibana-setup.sh`` (saved objects API, overwrite):

* "Aurelius activity": logins and changes per day (data views ``pyatlas-access``, time field ``loginTime``, and
  ``pyatlas-audit``, time field ``eventTime``);
* "Aurelius usage": how the frontend is used and how people navigate it (data view ``aurelius-clickstream``,
  time field ``viewTime``; see pyatlas/aurelius/clickstream.py).

Run ``python scripts/gen_kibana_dashboards.py`` after changing this file.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docker" / "kibana-dashboards.ndjson"
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


objects = [
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

usage = [
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


activity = dashboard("aurelius-activity", "Aurelius activity",
                     "Logins and changes per day (pyatlas access log and entity audits)",
                     [("aurelius-logins-per-day", 0, 0, 24, 14), ("aurelius-active-users-per-day", 24, 0, 24, 14),
                      ("aurelius-changes-per-day", 0, 14, 24, 14), ("aurelius-changes-per-user", 24, 14, 24, 14),
                      ("aurelius-changes-by-user-type", 0, 28, 24, 16), ("aurelius-logins-by-user", 24, 28, 24, 16)])
usage_dashboard = dashboard("aurelius-usage", "Aurelius usage",
                            "How the Aurelius frontend is used and how people navigate it (clickstream)",
                            [("usage-page-views-per-day", 0, 0, 24, 14), ("usage-visits-per-day", 24, 0, 24, 14),
                             ("usage-pages", 0, 14, 16, 15), ("usage-navigation", 16, 14, 16, 15),
                             ("usage-entry-pages", 32, 14, 16, 15), ("usage-time-on-page", 0, 29, 16, 15),
                             ("usage-searches", 16, 29, 16, 15), ("usage-entity-types", 32, 29, 16, 15),
                             ("usage-entities", 0, 44, 24, 16), ("usage-users", 24, 44, 24, 16)])

all_objects = [*objects, activity, *usage, usage_dashboard]
OUT.write_text("".join(json.dumps(o) + "\n" for o in all_objects), encoding="utf-8")
print(f"{OUT}: {len(all_objects)} saved objects")
