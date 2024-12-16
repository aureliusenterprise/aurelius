#!/bin/bash

echo "Running the Aurelius initialization script.."

# Sign elastic certificate
cd /home/appuser/;
yes | keytool -import -alias elasticca -file $SECRET_FILE_PATH -keypass elastic -keystore elastic.jks -storepass elastic;

# Wait for the Kafka Connect REST API to be available
while [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:${CONNECT_REST_PORT}/connectors)" != "200" ]; do
    echo "Waiting for the Kafka Connect REST API to be available...";
    sleep 5;
done;

# Deploy all workers
bash /tmp/aurelius/bin/deploy-all-workers.sh
