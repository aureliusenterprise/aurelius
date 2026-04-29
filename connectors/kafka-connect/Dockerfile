ARG VERSION
FROM ghcr.io/aureliusenterprise/aurelius-docker-kafka-connect-base:${VERSION}

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a Kafka Connect image with specific connectors and configurations for Aurelius Atlas."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius
LABEL org.opencontainers.image.title="Aurelius Kafka Connect"

# Install required plugins for Kafka Connect
ARG CONNECT_ELASTICSEARCH_VERSION=15.0.0 \
    CONNECT_TRANSFORMS_VERSION=latest

RUN confluent-hub install confluentinc/kafka-connect-elasticsearch:${CONNECT_ELASTICSEARCH_VERSION} --no-prompt && \
    confluent-hub install confluentinc/connect-transforms:${CONNECT_TRANSFORMS_VERSION} --no-prompt

# Set environment variables for Kafka Connect
ENV CONFIG_ELASTIC_KEYSTORE_LOCATION=/home/appuser/elastic.jks \
    CONFIG_ELASTIC_TRUSTSTORE_LOCATION=/home/appuser/elastic.jks

# Copy worker configurations into the Docker image
COPY ./connectors/kafka-connect/workers/ /tmp/aurelius/workers/

# Override the init script
COPY --chown=appuser:appuser --chmod=0500 connectors/kafka-connect/bin/ /tmp/aurelius/bin/
