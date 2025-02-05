#!/bin/bash

# Perform HTTP request and capture the response and the HTTP status code
response=$(curl -s -w "%{http_code}" http://localhost:8083/connectors?expand=status)
http_code=$(echo "$response" | tail -c 4)  # Extract the last 3 characters (HTTP code)
body=$(echo "$response" | head -c -4)      # Extract the body without the last 3 characters

# Get the state of each connector, make sure they are all running
status=$(echo "$body" | jq '.[] | .status | .connector | .state')
for s in $status; do
  if [ "$s" != "\"RUNNING\"" ]; then
    echo "Connectors not running"
    exit 1
  fi
done

echo "Connectors running"
exit 0
