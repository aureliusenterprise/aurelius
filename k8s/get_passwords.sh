#!/bin/bash

# to get the password to keycloak admin user:
KC_ADMIN_USERNAME=$(kubectl get secret keycloak-secret -o=jsonpath='{.data.admin-username}' -n ${1} | base64 --decode)
KC_ADMIN_PASSWORD=$(kubectl get secret keycloak-secret -o=jsonpath='{.data.admin-password}' -n ${1} | base64 --decode)

echo "keycloak admin:"
echo "username: ${KC_ADMIN_USERNAME}"
echo "password: ${KC_ADMIN_PASSWORD}"
echo "----"

# get keycloak passwords for the default  users of Atlas
ATLAS_ADMIN_USERNAME=$(kubectl get secret keycloak-secret-user-admin -o=jsonpath='{.data.username}' -n ${1} | base64 --decode)
ATLAS_ADMIN_PASSWORD=$(kubectl get secret keycloak-secret-user-admin -o=jsonpath='{.data.password}' -n ${1} | base64 --decode)

echo "atlas admin:"
echo "username: ${ATLAS_ADMIN_USERNAME}"
echo "password: ${ATLAS_ADMIN_PASSWORD}"
echo "----"

ATLAS_STEWARD_USERNAME=$(kubectl get secret keycloak-secret-user-steward -o=jsonpath='{.data.username}' -n ${1} | base64 --decode)
ATLAS_STEWARD_PASSWORD=$(kubectl get secret keycloak-secret-user-steward -o=jsonpath='{.data.password}' -n ${1} | base64 --decode)

echo "atlas steward:"
echo "username: ${ATLAS_STEWARD_USERNAME}"
echo "password: ${ATLAS_STEWARD_PASSWORD}"
echo "----"

ATLAS_DATA_SCIENTIST_USERNAME=$(kubectl get secret keycloak-secret-user-data -o=jsonpath='{.data.username}' -n ${1} | base64 --decode)
ATLAS_DATA_SCIENTIST_PASSWORD=$(kubectl get secret keycloak-secret-user-data -o=jsonpath='{.data.password}' -n ${1} | base64 --decode)

echo "atlas data scientist:"
echo "username: ${ATLAS_DATA_SCIENTIST_USERNAME}"
echo "password: ${ATLAS_DATA_SCIENTIST_PASSWORD}"
echo "=========="

# to get the password to elastic user:
echo "elasticsearch elastic user pwd: "
echo "username: elastic"
kubectl get secret elastic-search-es-elastic-user -o=jsonpath='{.data.elastic}' -n ${1} | base64 --decode; echo
echo "----"
