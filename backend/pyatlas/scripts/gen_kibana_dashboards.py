"""Writes ``docker/kibana-dashboards.ndjson``: the Kibana dashboard "Aurelius activity" (logins and changes per day)
with its Lens visualizations, imported by ``docker/kibana-setup.sh`` (saved objects API, overwrite).

Data views (created by kibana-setup.sh): ``pyatlas-access`` (logins, time field ``loginTime``) and
``pyatlas-audit`` (entity changes, time field ``eventTime``).  Run ``python scripts/gen_kibana_dashboards.py``
after changing this file.
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


def lens(obj_id, title, description, data_view, columns, order, visualization, vis_type):
    state = {
        "datasourceStates": {"formBased": {"layers": {LAYER: {"columns": columns, "columnOrder": order,
                                                               "incompleteColumns": {}, "sampling": 1}}}},
        "visualization": visualization, "query": {"query": "", "language": "kuery"}, "filters": [],
        "internalReferences": [], "adHocDataViews": {}}
    return {"type": "lens", "id": obj_id, "attributes": {"title": title, "description": description,
                                                         "visualizationType": vis_type, "state": state},
            "references": [{"type": "index-pattern", "id": data_view,
                            "name": f"indexpattern-datasource-layer-{LAYER}"}],
            "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.9.0"}


def xy(series_type, x, y, split=None):
    layer = {"layerId": LAYER, "layerType": "data", "seriesType": series_type, "xAccessor": x, "accessors": [y]}
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

layout = [("aurelius-logins-per-day", 0, 0, 24, 14), ("aurelius-active-users-per-day", 24, 0, 24, 14),
          ("aurelius-changes-per-day", 0, 14, 24, 14), ("aurelius-changes-per-user", 24, 14, 24, 14),
          ("aurelius-changes-by-user-type", 0, 28, 24, 16), ("aurelius-logins-by-user", 24, 28, 24, 16)]
panels, refs = [], []
for i, (obj_id, x, y, w, h) in enumerate(layout, 1):
    p = f"p{i}"
    panels.append({"type": "lens", "gridData": {"x": x, "y": y, "w": w, "h": h, "i": p}, "panelIndex": p,
                   "embeddableConfig": {"enhancements": {}}, "panelRefName": f"panel_{p}"})
    refs.append({"name": f"{p}:panel_{p}", "type": "lens", "id": obj_id})
dashboard = {"type": "dashboard", "id": "aurelius-activity",
             "attributes": {"title": "Aurelius activity", "description":
                            "Logins and changes per day (pyatlas access log and entity audits)",
                            "timeRestore": True, "timeFrom": "now-30d", "timeTo": "now", "refreshInterval":
                            {"pause": True, "value": 60000}, "panelsJSON": json.dumps(panels),
                            "optionsJSON": json.dumps({"useMargins": True, "syncColors": False, "syncCursor": True,
                                                       "syncTooltips": False, "hidePanelTitles": False}),
                            "kibanaSavedObjectMeta": {"searchSourceJSON": json.dumps(
                                {"query": {"query": "", "language": "kuery"}, "filter": []})}},
             "references": refs, "coreMigrationVersion": "8.8.0", "typeMigrationVersion": "8.9.0"}

OUT.write_text("".join(json.dumps(o) + "\n" for o in [*objects, dashboard]), encoding="utf-8")
print(f"{OUT}: {len(objects)} visualizations + dashboard")
