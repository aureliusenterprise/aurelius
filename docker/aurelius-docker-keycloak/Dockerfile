# syntax=docker/dockerfile:1

ARG KEYCLOAK_VERSION=22.0.5
FROM quay.io/keycloak/keycloak:${KEYCLOAK_VERSION}

ENV KC_HEALTH_ENABLED=true \
    KC_HTTP_PORT=8080 \
    KC_METRICS_ENABLED=true

COPY --chown=keycloak:root --chmod=755 ./docker/aurelius-docker-keycloak/themes /opt/keycloak/themes
