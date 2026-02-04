FROM aurelius-kafka-connect-jdbc-sink-base:local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Kafka Connect JDBC sink connector."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Kafka Connect JDBC Sink Example"

# Copy the connector configuration
COPY --chown=root:root --chmod=0755 connectors/aurelius-kafka-connect-jdbc-sink-example/workers/*.json /tmp/aurelius/workers/
