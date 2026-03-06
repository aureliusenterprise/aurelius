#!/bin/bash

/opt/keycloak/bin/kcadm.sh config credentials --server ${KEYCLOAK_SERVER_URL} --realm master --user ${KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME} --password ${KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD};
/opt/keycloak/bin/kcadm.sh create users -r ${KEYCLOAK_REALM_NAME} -s "username=${KEYCLOAK_USERNAME}" -s "enabled=true";
/opt/keycloak/bin/kcadm.sh set-password -r ${KEYCLOAK_REALM_NAME} --username ${KEYCLOAK_USERNAME} --new-password ${KEYCLOAK_ATLAS_ADMIN_PASSWORD};
/opt/keycloak/bin/kcadm.sh add-roles -r ${KEYCLOAK_REALM_NAME} --uusername ${KEYCLOAK_USERNAME} --rolename ROLE_ADMIN;
/opt/keycloak/bin/kcadm.sh add-roles -r ${KEYCLOAK_REALM_NAME} --uusername ${KEYCLOAK_USERNAME} --rolename DATA_STEWARD;
