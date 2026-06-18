#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/../certs"
ENV_FILE="$SCRIPT_DIR/../.env"

mkdir -p "$CERTS_DIR"

# Source the .env file to get environment variables
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

echo "[INFO] Using certs directory: $CERTS_DIR"

if [ ! -f "$CERTS_DIR/instances.yml" ]; then
  echo "[INFO] Creating instances.yml..."
	echo -ne \
	"instances:\n"\
	"  - name: es01\n"\
	"    dns:\n"\
	"      - elasticsearch\n"\
	"      - localhost\n"\
	"    ip:\n"\
	"      - 127.0.0.1\n"\
	"      - 172.17.0.1\n"\
	"  - name: kibana\n"\
	"    dns:\n"\
	"      - kibana\n"\
	"      - localhost\n"\
	"    ip:\n"\
	"      - 127.0.0.1\n"\
	"      - 172.17.0.1\n"\
	"  - name: enterprisesearch\n"\
	"    dns:\n"\
	"      - enterprisesearch\n"\
	"      - localhost\n"\
	"    ip:\n"\
	"      - 127.0.0.1\n"\
	"      - 172.17.0.1\n"\
	> $CERTS_DIR/instances.yml
  echo "[INFO] instances.yml created at $CERTS_DIR/instances.yml"
fi

ES_IMAGE="docker.elastic.co/elasticsearch/elasticsearch:$ELASTIC_STACK_VERSION"

docker run --rm -i -u root -e ENTERPRISE_SEARCH_SSL_KEYSTORE_PASSWORD="$ENTERPRISE_SEARCH_SSL_KEYSTORE_PASSWORD" -v "$CERTS_DIR:/certs" $ES_IMAGE bash -c '
	if [ ! -f /certs/ca.zip ]; then
		echo "[INFO] Creating CA..."
		bin/elasticsearch-certutil ca --silent --pem -out /certs/ca.zip
		unzip -j -o /certs/ca.zip -d /certs/ca
		echo "[INFO] CA created in /certs/ca"
	fi;

	if [ ! -f /certs/certs.zip ]; then
		echo "[INFO] Generating instance certs..."
		elasticsearch-certutil cert --silent --pem -out /certs/certs.zip --in /certs/instances.yml --ca-cert /certs/ca/ca.crt --ca-key /certs/ca/ca.key
		unzip -j -o /certs/certs.zip -d /certs/certs
		echo "[INFO] Certificates generated in /certs"
	fi;

	if [ ! -f /certs/certs/enterprisesearch.p12 ]; then
		echo "[INFO] Converting enterprisesearch cert to PKCS12..."
		openssl pkcs12 -export -in /certs/certs/enterprisesearch.crt -inkey /certs/certs/enterprisesearch.key -out /certs/certs/enterprisesearch.p12 -name enterprisesearch -passout env:ENTERPRISE_SEARCH_SSL_KEYSTORE_PASSWORD
		chmod 644 /certs/certs/enterprisesearch.p12
		echo "[INFO] PKCS12 keystore created in /certs/certs/enterprisesearch.p12"
	fi;

	# Ensure keystore remains readable by the Enterprise Search runtime user.
	if [ -f /certs/certs/enterprisesearch.p12 ]; then
		chmod 644 /certs/certs/enterprisesearch.p12
	fi;
'

echo "[INFO] Certificate generation complete. Files are in $CERTS_DIR."
