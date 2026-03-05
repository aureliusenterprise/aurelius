#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/../certs"

mkdir -p "$CERTS_DIR"

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
	> $CERTS_DIR/instances.yml
  echo "[INFO] instances.yml created at $CERTS_DIR/instances.yml"
fi

ES_IMAGE="docker.elastic.co/elasticsearch/elasticsearch:$ELASTIC_STACK_VERSION"

docker run --rm -i -v "$CERTS_DIR:/certs" $ES_IMAGE bash -c '
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
'

echo "[INFO] Certificate generation complete. Files are in $CERTS_DIR."
