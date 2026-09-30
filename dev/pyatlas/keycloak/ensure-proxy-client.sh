#!/bin/bash
# Replaces a default Keycloak admin password by KEYCLOAK_ADMIN_PASSWORD (a Keycloak started before the secrets were
# generated).  Idempotent, runs at every "docker compose up" (service keycloak-init).  Realms, clients and the realm
# settings of the tenants are managed by aurelius-admin (backend/pyatlas/pyatlas/tenant_admin.py, service
# aurelius-init).
#   KEYCLOAK_URL, KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD
set -euo pipefail
KCADM=/opt/keycloak/bin/kcadm.sh
[ -x "$KCADM" ] || KCADM=kcadm.sh

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

echo "keycloak-init: admin login ok"
