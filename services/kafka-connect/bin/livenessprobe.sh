#!/bin/bash

# Perform HTTP request and capture the response and the HTTP status code
response=$(curl -s -w "%{http_code}" http://localhost:8083/connectors?expand=status)
http_code=$(echo "$response" | tail -c 4)  # Extract the last 3 characters (HTTP code)
body=$(echo "$response" | head -c -4)      # Extract the body without the last 3 characters

# Check whether the tasks of all the connectors are running
status=$(echo "$body" | jq '.[] | .status | .tasks | .[] | .state')
for s in $status; do
  if [ "$s" != "\"RUNNING\"" ]; then
    echo "Connectors not running"
    exit 1
  fi
done

echo "Connectors running"
exit 0
