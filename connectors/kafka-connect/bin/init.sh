#!/bin/bash

echo "Running the Aurelius initialization script..."

# Load environment variables into a config file for use in the connector configuration
ENV_FILE="/tmp/aurelius/env"

echo "# Environment variables (auto-generated)" > ${ENV_FILE}
env | while read -r VAR
do
    if [[ ${VAR} =~ ^CONFIG ]]; then
          echo ${VAR} >> ${ENV_FILE}
    fi
done

# Import the SSL certificate into the Java keystore
yes | keytool -import -alias elasticca -file $SECRET_FILE_PATH -keypass $CONFIG_ELASTIC_KEY_PASSWORD -keystore $CONFIG_ELASTIC_KEYSTORE_LOCATION -storepass $CONFIG_ELASTIC_KEYSTORE_PASSWORD;

# Wait for the Kafka Connect REST API to be available
while [ "$(curl -s -w "%{http_code}" http://${CONNECT_REST_ADVERTISED_HOST_NAME}:${CONNECT_REST_PORT}/connectors | tail -c 3)" != "200" ]; do echo "Waiting for the Kafka Connect REST API to be available..."; sleep 5; done;

# Deploy all workers
bash /tmp/aurelius/bin/deploy-all-workers.sh
