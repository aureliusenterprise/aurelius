#!/bin/bash
# Makes sure the realm has the confidential client the reverse proxy uses to protect admin tools (Kibana) with a
# Keycloak login.  Idempotent, runs at every "docker compose up" (service keycloak-init) - also for realms that
# were imported before the client existed.  Admin tools require the realm role ROLE_ADMIN (claim "roles").
#   KEYCLOAK_URL, KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, REALM (m4i), PROXY_CLIENT_ID (aurelius_proxy),
#   PROXY_CLIENT_SECRET, PUBLIC_URL (the URL the browser uses)
set -euo pipefail
KCADM=/opt/keycloak/bin/kcadm.sh
[ -x "$KCADM" ] || KCADM=kcadm.sh
REALM="${REALM:-m4i}"
CLIENT="${PROXY_CLIENT_ID:-aurelius_proxy}"

for i in $(seq 1 60); do
  if $KCADM config credentials --server "$KEYCLOAK_URL" --realm master --user "$KEYCLOAK_ADMIN" \
       --password "$KEYCLOAK_ADMIN_PASSWORD" >/dev/null 2>&1; then break; fi
  echo "keycloak-init: waiting for Keycloak ($i)"; sleep 5
done

body=$(cat <<JSON
{"clientId": "$CLIENT", "name": "Aurelius reverse proxy (admin tools)", "enabled": true, "protocol": "openid-connect",
 "publicClient": false, "secret": "$PROXY_CLIENT_SECRET", "standardFlowEnabled": true,
 "directAccessGrantsEnabled": false, "serviceAccountsEnabled": false,
 "redirectUris": ["$PUBLIC_URL/aurelius/kibana/*"], "webOrigins": ["+"],
 "attributes": {"post.logout.redirect.uris": "$PUBLIC_URL/aurelius/*"},
 "protocolMappers": [{"name": "realm roles as roles", "protocol": "openid-connect",
   "protocolMapper": "oidc-usermodel-realm-role-mapper", "consentRequired": false,
   "config": {"multivalued": "true", "claim.name": "roles", "jsonType.label": "String", "id.token.claim": "true",
              "access.token.claim": "true", "userinfo.token.claim": "true"}}]}
JSON
)
id=$($KCADM get clients -r "$REALM" -q clientId="$CLIENT" --fields id --format csv --noquotes 2>/dev/null | head -1)
if [ -z "$id" ]; then
  echo "$body" | $KCADM create clients -r "$REALM" -f - >/dev/null
  echo "keycloak-init: client $CLIENT created"
else
  # keep the configuration in step (secret, redirect URL) without touching anything else
  $KCADM update "clients/$id" -r "$REALM" -s "secret=$PROXY_CLIENT_SECRET" \
    -s "redirectUris=[\"$PUBLIC_URL/aurelius/kibana/*\"]" >/dev/null
  echo "keycloak-init: client $CLIENT up to date"
fi
