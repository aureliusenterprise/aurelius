#!/bin/bash

# Generate the configuration file for the Aurelius frontend application and place it in the correct location
CONFIG_FILE_PATH="/usr/share/nginx/html/config.json"
TEMPLATE_PATH=$(dirname "$0")/config.json.template
echo $(envsubst < $TEMPLATE_PATH) > $CONFIG_FILE_PATH
