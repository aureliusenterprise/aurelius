#!/usr/bin/env bash
TOKEN=$(./oauth.sh --endpoint "${KEYCLOAK_SERVER_URL}realms/m4i/protocol/openid-connect/token" \
--client-id "$KEYCLOAK_CLIENT_ID" \
--access "$KEYCLOAK_USERNAME" "$KEYCLOAK_ATLAS_ADMIN_PASSWORD")

python export_atlas.py --token "$TOKEN" \
--base-url "$ATLAS_SERVER_URL" \
--output "data/sample_data.zip" --import-data
