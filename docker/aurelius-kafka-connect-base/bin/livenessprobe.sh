#!/bin/bash

# Perform HTTP request and capture the response and the HTTP status code
if [ -z "${CONNECT_REST_ADVERTISED_HOST_NAME}" ]; then
    CONNECT_REST_ADVERTISED_HOST_NAME=$(hostname -i)
fi

response=$(curl -s -w "%{http_code}" ${CONNECT_REST_ADVERTISED_HOST_NAME}:${CONNECT_REST_PORT}/connectors?expand=status)
http_code=$(echo "$response" | tail -c 4)  # Extract the last 3 characters (HTTP code)
body=$(echo "$response" | head -c -4)      # Extract the body without the last 3 characters

if [ "$http_code" != "200" ]; then
  echo "ERROR Kafka Connect not running. Http code: ${http_code}" >> /proc/1/fd/1
  exit 1
fi

if [ "$body" == "{}" ]; then
  echo "ERROR No connectors deployed" >> /proc/1/fd/1
  exit 1
fi

# Check whether the tasks of all the connectors are running
status=$(echo "$body" | jaq '.[] | .status | .connector | .state')

for s in $status; do
  if [ "$s" != "\"RUNNING\"" ]; then
    echo "ERROR Connectors not running" >> /proc/1/fd/1
    exit 1
  fi
done

status=$(echo "$body" | jaq '.[] | .status | .tasks | .[] | .state')

for s in $status; do
  if [ "$s" != "\"RUNNING\"" ]; then
    echo "ERROR Connector tasks not running" >> /proc/1/fd/1
    exit 1
  fi
done

echo "INFO Connectors running" >> /proc/1/fd/1
exit 0
