#!/bin/bash

# Default values
DEFAULT_KAFKA_CONNECT_URL="http://localhost:${CONNECT_REST_PORT}"

WORKER_FILE=$1
KAFKA_CONNECT_URL=${2:-$DEFAULT_KAFKA_CONNECT_URL}

# Check if the worker file is provided
if [ -z "$WORKER_FILE" ]; then
    echo "Missing worker file path parameter at position 1"
    exit 1
fi

# Derive the worker name from the file name
NAME=$(basename "$WORKER_FILE" .json)

# Read the file content
WORKER=$(cat "$WORKER_FILE")

# Check if ELASTICSEARCH_URL is set
if [[ -n "$ELASTICSEARCH_URL" ]]; then
  WORKER=$(echo "$WORKER" | sed "s#\"connection.url\": \".*\"#\"connection.url\": \"$ELASTICSEARCH_URL\"#")
  echo "Replaced connection.url with ELASTICSEARCH_URL value: $ELASTICSEARCH_URL"
fi
# Check if kafka_connect_elastic_password is set
if [[ -n "$KAFKA_CONNECT_ELASTIC_PASSWORD" ]]; then
  WORKER=$(echo "$WORKER" | sed "s#\"connection.password\": \".*\"#\"connection.password\": \"$KAFKA_CONNECT_ELASTIC_PASSWORD\"#")
  echo "Replaced connection.password with ELASTIC_PASSWORD value."
fi

echo "Deploying worker $NAME to $KAFKA_CONNECT_URL/connectors/$NAME/config"

# Update the worker on Kafka Connect
curl -X PUT "$KAFKA_CONNECT_URL/connectors/$NAME/config" \
     -H "Content-Type: application/json" \
     -d "$WORKER"

echo "Done deploying worker $NAME"
