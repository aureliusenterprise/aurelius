#!/bin/bash
# Initialize Grafana data directory with dashboards from the config folder.
# This script runs on first startup to populate the volume with dashboard JSON files.

set -ex

GRAFANA_HOME="/grafana"
DASHBOARDS_SOURCE="/dashboards-ro"
DASHBOARDS_DEST="${GRAFANA_HOME}/dashboards"

echo "=== Initializing Grafana ==="

# Ensure directories exist (hardened image may not create them)
mkdir -p "${GRAFANA_HOME}/data"
mkdir -p "${GRAFANA_HOME}/logs"
mkdir -p "${GRAFANA_HOME}/plugins"
mkdir -p "${DASHBOARDS_DEST}"

# Copy dashboards from source to destination if needed
if [ -d "${DASHBOARDS_SOURCE}" ]; then
    # Count files in source
    SOURCE_COUNT=$(find "${DASHBOARDS_SOURCE}" -name "*.json" | wc -l)

    # Count files in destination
    DEST_COUNT=$(find "${DASHBOARDS_DEST}" -name "*.json" 2>/dev/null | wc -l)

    if [ "${SOURCE_COUNT}" -gt 0 ] && [ "${DEST_COUNT}" -eq 0 ]; then
        echo "Copying ${SOURCE_COUNT} dashboard(s) from ${DASHBOARDS_SOURCE} to ${DASHBOARDS_DEST}"
        cp "${DASHBOARDS_SOURCE}"/*.json "${DASHBOARDS_DEST}/"
    else
        echo "Dashboards already present (${DEST_COUNT} files), skipping copy"
    fi
else
    echo "WARNING: No dashboards source found at ${DASHBOARDS_SOURCE}"
fi

echo "=== Grafana initialization complete ==="
