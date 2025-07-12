#!/bin/bash

echo "Running the Aurelius initialization script..."

ENV_FILE="/tmp/aurelius/env"

echo "# Environment variables (auto-generated)" > ${ENV_FILE}
env | while read -r VAR
do
    if [[ ${VAR} =~ ^CONFIG ]]; then
          echo ${VAR} >> ${ENV_FILE}
    fi
done

# Wait for the Kafka Connect REST API to be available
while [ "$(curl -s -w "%{http_code}" http://${CONNECT_REST_ADVERTISED_HOST_NAME}:${CONNECT_REST_PORT}/connectors | tail -c 3)" != "200" ]; do echo "Waiting for the Kafka Connect REST API to be available..."; sleep 5; done;

# Deploy all workers
bash /tmp/aurelius/bin/deploy-all-workers.sh
