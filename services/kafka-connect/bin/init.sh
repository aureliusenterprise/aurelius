#!/bin/bash

echo "Running the Aurelius initialization script.."

# Sign elastic certificate
cd /home/appuser/;
yes | keytool -import -alias elasticca -file certs/ca/ca.crt -keypass elastic -keystore elastic.jks -storepass elastic | tee error.log;

# Wait for the Kafka Connect REST API to be available
while [ "$(curl -s http://localhost:${CONNECT_REST_PORT}/connectors)" != "[]" ]; do echo "Waiting for the Kafka Connect REST API to be available..." >> error.log; sleep 5; done;

# Deploy all workers
bash /tmp/aurelius/bin/deploy-all-workers.sh
