#!/usr/bin/env bash
OUTPUT_FILE="${1:-sample_data.zip}"

DIR="$(cd "$(dirname "$0")" && pwd)"

TOKEN=$("$DIR/oauth.sh" --endpoint "${KEYCLOAK_SERVER_URL}realms/${KEYCLOAK_REALM_NAME}/protocol/openid-connect/token" \
--client-id "$KEYCLOAK_CLIENT_ID" \
--access "$KEYCLOAK_USERNAME" "$KEYCLOAK_ATLAS_ADMIN_PASSWORD")

python "$DIR/../scripts/export_atlas.py" --token "$TOKEN" \
--base-url "$ATLAS_SERVER_URL" \
--output "$DIR/../data/$OUTPUT_FILE" --import-data
