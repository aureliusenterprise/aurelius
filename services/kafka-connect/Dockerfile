ARG CONNECT_VERSION=latest
FROM confluentinc/cp-kafka-connect:${CONNECT_VERSION}

LABEL org.opencontainers.image.source https://github.com/aureliusenterprise/aurelius

USER root

# Install gettext for envsubst
RUN yum update -y && yum install -y gettext

USER appuser

ARG CONNECT_ELASTICSEARCH_VERSION=latest
RUN confluent-hub install confluentinc/kafka-connect-elasticsearch:${CONNECT_ELASTICSEARCH_VERSION} --no-prompt

ARG CONNECT_TRANSFORMS_VERSION=latest
RUN confluent-hub install confluentinc/connect-transforms:${CONNECT_TRANSFORMS_VERSION} --no-prompt

# Copy the scripts and connector files into the Docker image
COPY --chmod=755 ./services/kafka-connect/bin/ /tmp/aurelius/bin/
COPY ./services/kafka-connect/workers/ /tmp/aurelius/workers/

ENTRYPOINT ["/tmp/aurelius/bin/docker-entrypoint.sh"]
