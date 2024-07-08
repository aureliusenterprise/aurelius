#!/bin/bash

echo "Running the Aurelius initialization script.."

# Sign elastic certificate
cd /home/appuser/;
yes | keytool -import -alias elasticca -file certs/ca/ca.crt -keypass elastic -keystore elastic.jks -storepass elastic | tee error.log;

# Wait for the Kafka Connect REST API to be available
while [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:${CONNECT_REST_PORT}/connectors)" != "200" ]; do
    echo "Waiting for the Kafka Connect REST API to be available...";
    sleep 5;
done;

# Deploy all workers
bash /tmp/aurelius/bin/deploy-all-workers.sh
