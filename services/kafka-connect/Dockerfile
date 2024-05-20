ARG CONNECT_VERSION=latest
FROM confluentinc/cp-kafka-connect:${CONNECT_VERSION}

ARG CONNECT_ELASTICSEARCH_VERSION=latest
RUN confluent-hub install confluentinc/kafka-connect-elasticsearch:${CONNECT_ELASTICSEARCH_VERSION} --no-prompt

ARG CONNECT_TRANSFORMS_VERSION=latest
RUN confluent-hub install confluentinc/connect-transforms:${CONNECT_TRANSFORMS_VERSION} --no-prompt
