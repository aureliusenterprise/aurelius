FROM aurelius-kafka-connect-base:local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a base image for Kafka Connect that includes the JDBC sink connector."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Kafka Connect JDBC Sink Base"

USER root

# Download Debezium
ARG DEBEZIUM_CONNECTOR_JDBC_VERSION=3.1.2.Final
ADD --chown=root:root --chmod=0755 https://repo1.maven.org/maven2/io/debezium/debezium-connector-jdbc/${DEBEZIUM_CONNECTOR_JDBC_VERSION}/debezium-connector-jdbc-${DEBEZIUM_CONNECTOR_JDBC_VERSION}-plugin.tar.gz /usr/share/confluent-hub-components/

# Install Debezium
RUN tar -xvf /usr/share/confluent-hub-components/debezium-connector-jdbc-${DEBEZIUM_CONNECTOR_JDBC_VERSION}-plugin.tar.gz \
    -C /usr/share/confluent-hub-components/ && \
    chown -R appuser:appuser /usr/share/confluent-hub-components

USER appuser

ENV CONNECT_CONNECTOR_CLIENT_CONFIG_OVERRIDE_POLICY=All
