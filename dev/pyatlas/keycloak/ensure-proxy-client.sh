#!/bin/bash
# Makes sure the realm has the confidential client the reverse proxy uses to protect admin tools (Kibana) with a
# Keycloak login, applies the realm's security settings and replaces a default admin password.  Idempotent, runs at every "docker compose up" (service keycloak-init) - also for realms that
# were imported before the client existed.  Admin tools require the realm role ROLE_ADMIN (claim "roles").
#   KEYCLOAK_URL, KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD, REALM (m4i), PROXY_CLIENT_ID (aurelius_proxy),
#   PROXY_CLIENT_SECRET, PUBLIC_URL (the URL the browser uses)
set -euo pipefail
KCADM=/opt/keycloak/bin/kcadm.sh
[ -x "$KCADM" ] || KCADM=kcadm.sh
REALM="${REALM:-m4i}"
CLIENT="${PROXY_CLIENT_ID:-aurelius_proxy}"

login() {  # login <password>
  $KCADM config credentials --server "$KEYCLOAK_URL" --realm master --user "$KEYCLOAK_ADMIN" \
    --password "$1" >/dev/null 2>&1
}
ok=""
for i in $(seq 1 60); do
  if login "$KEYCLOAK_ADMIN_PASSWORD"; then ok=1; break; fi
  # a Keycloak started before the secrets were generated still has the old default admin password: replace it
  if [ "$KEYCLOAK_ADMIN_PASSWORD" != "admin" ] && login "admin"; then
    $KCADM set-password -r master --username "$KEYCLOAK_ADMIN" --new-password "$KEYCLOAK_ADMIN_PASSWORD"
    echo "keycloak-init: default admin password replaced by KEYCLOAK_ADMIN_PASSWORD"
    login "$KEYCLOAK_ADMIN_PASSWORD" && { ok=1; break; }
  fi
  echo "keycloak-init: waiting for Keycloak ($i)"; sleep 5
done
[ -n "$ok" ] || { echo "keycloak-init: cannot log in to Keycloak as $KEYCLOAK_ADMIN"; exit 1; }

# realm hardening, also for realms imported before these settings were in realm-m4i.json
$KCADM update "realms/$REALM" -s sslRequired=external -s bruteForceProtected=true -s failureFactor=10 \
  -s waitIncrementSeconds=60 -s maxFailureWaitSeconds=900 -s 'passwordPolicy=length(8) and notUsername' >/dev/null
echo "keycloak-init: realm $REALM settings up to date (brute force protection, password policy)"

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
