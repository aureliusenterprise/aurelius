#!/bin/sh
# Creates Kibana data views for the pyatlas indices (run once by the "kibana-setup" service of docker-compose).
# Idempotent: data views have fixed ids and are overwritten on every run.
#
#   KIBANA_URL    default http://kibana:5601
#   INDEX_PREFIX  default atlas   (= PYATLAS_ES_INDEX_PREFIX)
set -eu
KIBANA_URL="${KIBANA_URL:-http://kibana:5601}"
P="${INDEX_PREFIX:-atlas}"

echo "kibana-setup: waiting for Kibana at $KIBANA_URL ..."
i=0
until curl -sf "$KIBANA_URL/api/status" | grep -q '"level":"available"'; do
  i=$((i + 1))
  if [ "$i" -gt 180 ]; then echo "kibana-setup: Kibana did not become available"; exit 1; fi
  sleep 5
done

# pyatlas stores times as epoch milliseconds (long); a runtime "date" field makes them usable as time field
rt() {  # rt <runtime field name> <source field>
  printf '"%s": {"type": "date", "script": {"source": "if (doc.containsKey(\\"%s\\") && doc[\\"%s\\"].size() > 0) emit(doc[\\"%s\\"].value);"}}' "$1" "$2" "$2" "$2"
}

view() {  # view <id> <index pattern> <name> <time field or ""> <runtime fields json>
  if [ -n "$4" ]; then tf="\"timeFieldName\": \"$4\","; else tf=""; fi
  body=$(printf '{"override": true, "data_view": {"id": "%s", "title": "%s", "name": "%s", %s "allowNoIndex": true, "runtimeFieldMap": {%s}}}' "$1" "$2" "$3" "$tf" "$5")
  code=$(curl -s -o /tmp/resp.json -w '%{http_code}' -X POST "$KIBANA_URL/api/data_views/data_view" \
         -H 'kbn-xsrf: pyatlas' -H 'Content-Type: application/json' -d "$body")
  if [ "$code" = "200" ]; then echo "kibana-setup: data view '$3' ($2) ok"; else echo "kibana-setup: '$3' failed ($code): $(cat /tmp/resp.json)"; fi
}

view "pyatlas-entities"      "${P}_entities"      "Atlas entities"             "updated"   "$(rt updated updateTime), $(rt created createTime)"
view "pyatlas-relationships" "${P}_relationships" "Atlas relationships"        "updated"   "$(rt updated updateTime), $(rt created createTime)"
view "pyatlas-audit"         "${P}_audit"         "Atlas entity audits"        "eventTime" "$(rt eventTime timestamp)"
view "pyatlas-typedefs"      "${P}_typedefs"      "Atlas type definitions"     "updated"   "$(rt updated updateTime)"
view "pyatlas-meta"          "${P}_meta"          "Atlas server state (admin audits, metrics, saved searches, tasks)" "updated" "$(rt updated updateTime)"
view "pyatlas-unique"        "${P}_unique"        "Atlas unique attribute keys" "" ""
view "aurelius-search"       "${P}_aurelius_atlas_dev"             "Aurelius search documents (atlas-dev)"      "" ""
view "aurelius-quality"      "${P}_aurelius_atlas_dev_quality"     "Aurelius data quality (atlas-dev-quality)" "" ""
view "aurelius-gov-quality"  "${P}_aurelius_atlas_dev_gov_quality" "Aurelius governance quality (atlas-dev-gov-quality)" "" ""
view "pyatlas-all"           "${P}_*"             "Atlas (all indices)"        ""          ""

# entities as default data view; Discover shows the last 10 years by default (the data is not a time series)
curl -s -o /dev/null -X POST "$KIBANA_URL/api/data_views/default" -H 'kbn-xsrf: pyatlas' \
     -H 'Content-Type: application/json' -d '{"data_view_id": "pyatlas-entities", "force": true}'
curl -s -o /dev/null -X POST "$KIBANA_URL/api/kibana/settings" -H 'kbn-xsrf: pyatlas' -H 'Content-Type: application/json' \
     -d '{"changes": {"timepicker:timeDefaults": "{\"from\": \"now-10y\", \"to\": \"now\"}"}}'
echo "kibana-setup: done - open $KIBANA_URL/app/discover"
