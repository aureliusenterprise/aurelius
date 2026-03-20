#!/bin/bash

# to get the password to keycloak admin user:
KC_ADMIN_USERNAME=$(kubectl get secret keycloak-secret -o=jsonpath='{.data.admin-username}' -n ${1} | base64 --decode)
KC_ADMIN_PASSWORD=$(kubectl get secret keycloak-secret -o=jsonpath='{.data.admin-password}' -n ${1} | base64 --decode)

echo "keycloak admin:"
echo "username: ${KC_ADMIN_USERNAME}"
echo "password: ${KC_ADMIN_PASSWORD}"
echo "----"
# get keycloak passwords for the default  users of Atlas
echo "atlas admin user:"
echo "username: atlas"
kubectl get secret keycloak-secret-user-admin -o=jsonpath='{.data.password}' -n ${1} | base64 --decode; echo
echo "----"
echo "keycloak Atlas data steward user pwd: "
echo "username: steward"
kubectl get secret keycloak-secret-user-steward -o=jsonpath='{.data.password}' -n ${1} | base64 --decode; echo
echo "----"
echo "keycloak Atlas data user pwd: "
echo "username: scientist"
kubectl get secret keycloak-secret-user-data -o=jsonpath='{.data.password}' -n ${1} | base64 --decode; echo
echo "=========="
# to get the password to elastic user:
echo "elasticsearch elastic user pwd: "
echo "username: elastic"
kubectl get secret elastic-search-es-elastic-user -o=jsonpath='{.data.elastic}' -n ${1} | base64 --decode; echo
echo "----"
