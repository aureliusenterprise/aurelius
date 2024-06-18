#!/bin/bash

# Default values
DEFAULT_WORKER_DIR="/tmp/aurelius/workers"
DEFAULT_KAFKA_CONNECT_URL="http://localhost:${CONNECT_REST_PORT}"

WORKER_DIR=${1:-$DEFAULT_WORKER_DIR}
KAFKA_CONNECT_URL=${2:-$DEFAULT_KAFKA_CONNECT_URL}

echo "Deploying all workers in $WORKER_DIR to $KAFKA_CONNECT_URL ..."

# Loop through all JSON files in the worker directory
for file in "$WORKER_DIR"/*.json; do
    # Update the worker
    /tmp/aurelius/bin/deploy-worker.sh "$file" "$KAFKA_CONNECT_URL"
done

echo "Done deploying all workers"
