#!/bin/bash

# Path to the enterprise search configuration file
CONFIG_FILE="/usr/share/enterprise-search/config/enterprise-search.yml"

# Setting to be added
SETTING="app_search.engine.total_fields.limit: 96"

# Check if the setting already exists in the configuration file
if ! grep -qxF "$SETTING" "$CONFIG_FILE"; then
  echo "$SETTING" >> "$CONFIG_FILE"
  echo "Setting added to $CONFIG_FILE"
else
  echo "Setting already exists in $CONFIG_FILE"
fi