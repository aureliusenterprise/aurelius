#!/usr/bin/env bash
OUTPUT_FILE="${1:-sample_data.zip}"

TOKEN=$(./oauth.sh --endpoint "${KEYCLOAK_SERVER_URL}realms/${KEYCLOAK_REALM_NAME}/protocol/openid-connect/token" \
--client-id "$KEYCLOAK_CLIENT_ID" \
--access "$KEYCLOAK_USERNAME" "$KEYCLOAK_ATLAS_ADMIN_PASSWORD")

python ../scripts/export_atlas.py --token "$TOKEN" \
--base-url "$ATLAS_SERVER_URL" \
--output "../data/$OUTPUT_FILE" --import-data
