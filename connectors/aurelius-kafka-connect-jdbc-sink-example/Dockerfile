ARG CONNECT_VERSION=8.2.0
ARG KAFKA_VERSION=4.3-debian13

# Use a Confluent image for the build stage
FROM confluentinc/cp-kafka-connect:${CONNECT_VERSION} AS builder

# Switch to the root user
USER root

# Install build tools
RUN --mount=type=cache,target="/var/cache/dnf",sharing="locked" \
    microdnf install -y gzip tar

# Install Apache AVRO converter
ARG CONNECT_AVRO_CONVERTER_VERSION=8.2.0
RUN confluent-hub install "confluentinc/kafka-connect-avro-converter:${CONNECT_AVRO_CONVERTER_VERSION}" --no-prompt

# Download Debezium
ARG DEBEZIUM_CONNECTOR_JDBC_VERSION=3.5.1.Final
ADD "https://repo1.maven.org/maven2/io/debezium/debezium-connector-jdbc/${DEBEZIUM_CONNECTOR_JDBC_VERSION}/debezium-connector-jdbc-${DEBEZIUM_CONNECTOR_JDBC_VERSION}-plugin.tar.gz" "/usr/share/confluent-hub-components/"

# Install Debezium
RUN tar -xvf "/usr/share/confluent-hub-components/debezium-connector-jdbc-${DEBEZIUM_CONNECTOR_JDBC_VERSION}-plugin.tar.gz" -C "/usr/share/confluent-hub-components/"

# Use a hardened Kafka image during runtime
# Note: the hardened image does not have a package manager
FROM dhi.io/kafka:${KAFKA_VERSION} AS runtime

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Kafka Connect JDBC sink connector."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Kafka Connect JDBC Sink Example"
LABEL org.opencontainers.image.version="${VERSION}"

# Copy runtime dependencies from the builder stage
COPY --chown=root:root --chmod=0755 --from=builder "/usr/share/confluent-hub-components" "/usr/share/confluent-hub-components"

# Switch to the non-root user
USER kafka
