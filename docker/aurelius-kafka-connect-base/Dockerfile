ARG CONNECT_VERSION=8.1.1
FROM confluentinc/cp-kafka-connect:${CONNECT_VERSION}

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a base image for Kafka Connect with common plugins and healthchecks."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Kafka Connect Base"

USER root

# Install dependencies
ARG CONNECT_AVRO_CONVERTER_VERSION=8.1.1

RUN confluent-hub install confluentinc/kafka-connect-avro-converter:"${CONNECT_AVRO_CONVERTER_VERSION}" --no-prompt && \
    chown -R appuser:appuser /usr/share/confluent-hub-components && \
    mkdir /tmp/aurelius && \
    touch /tmp/aurelius/env && \
    chown appuser:appuser /tmp/aurelius/env && \
    chmod 755 /tmp/aurelius/env && \
    curl -fsSL https://github.com/01mf02/jaq/releases/latest/download/jaq-$(uname -m)-unknown-linux-musl -o jaq && chmod +x jaq && \
    mv jaq /usr/local/bin/

USER appuser

# Copy the scripts into the Docker image
COPY --chmod=0755 docker/aurelius-kafka-connect-base/bin/ /tmp/aurelius/bin/

# Check the health of the connector by running the liveness probe script every 10 seconds
HEALTHCHECK --interval=10s --timeout=10s --retries=30 \
    CMD ["/tmp/aurelius/bin/livenessprobe.sh"]

# Start the Kafka Connect service
ENTRYPOINT ["/tmp/aurelius/bin/docker-entrypoint.sh"]
