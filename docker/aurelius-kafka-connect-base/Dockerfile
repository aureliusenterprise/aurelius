ARG CONNECT_VERSION=7.9.1
FROM confluentinc/cp-kafka-connect:${CONNECT_VERSION}

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a common base image for Kafka Connect."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius
LABEL org.opencontainers.image.title="Aurelius Kafka Connect Base"

# Switch to root user to install necessary packages and tools
USER root

RUN chown -R appuser:appuser /usr/share/confluent-hub-components && \
    mkdir /tmp/aurelius && \
    touch /tmp/aurelius/env && \
    chown appuser:appuser /tmp/aurelius/env && \
    chmod 755 /tmp/aurelius/env && \
    curl -fsSL https://github.com/01mf02/jaq/releases/latest/download/jaq-$(uname -m)-unknown-linux-musl -o jaq && chmod +x jaq && \
    mv jaq /usr/local/bin/

# Switch back to the non-root user
USER appuser

# Copy the scripts into the Docker image
COPY --chown=appuser:appuser --chmod=0500 docker/aurelius-kafka-connect-base/bin/ /tmp/aurelius/bin/

# Check the health of the connector by running the liveness probe script every 10 seconds
HEALTHCHECK --interval=10s --timeout=10s --retries=30 \
    CMD ["/tmp/aurelius/bin/livenessprobe.sh"]

# Start the Kafka Connect service
ENTRYPOINT ["/tmp/aurelius/bin/docker-entrypoint.sh"]
