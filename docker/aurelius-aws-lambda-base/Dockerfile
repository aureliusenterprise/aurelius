# syntax=docker/dockerfile:1

ARG BUILDER_IMAGE_VERSION=3.14-debian13-dev
ARG RUNTIME_IMAGE_VERSION=3.14-debian13

# Use a hardened Python image with dev tools for the build stage.
FROM dhi.io/python:${BUILDER_IMAGE_VERSION} AS builder

# Set the working directory
WORKDIR /build

# Install build dependencies and tools. Use a cache mount to speed up repeated builds.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y cpio rpm

# Install the Lambda Insights extension.
COPY docker/aurelius-aws-lambda-base/extensions/lambda-insights-extension.rpm \
    /tmp/lambda-insights-extension.rpm

RUN mkdir -p /tmp/insights && \
    rpm2cpio /tmp/lambda-insights-extension.rpm | cpio -idmv -D /tmp/insights && \
    mkdir -p /opt/cloudwatch && \
    cp -r /tmp/insights/opt/extensions/. /opt/cloudwatch/ && \
    rm -rf /tmp/insights /tmp/lambda-insights-extension.rpm

# Install AWS Lambda dependencies for Python. Use a cache mount to speed up repeated builds.
ARG AWS_LAMBDA_RIC_VERSION=4.0.0

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --only-binary=:all: --target=./ awslambdaric==${AWS_LAMBDA_RIC_VERSION}

# Use a hardened Python image for the final application image.
FROM dhi.io/python:${RUNTIME_IMAGE_VERSION} AS runtime

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a base image for AWS Lambda functions."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius AWS Lambda Base"
LABEL org.opencontainers.image.version="${VERSION}"

# Set the working directory
WORKDIR /var/task

# Copy awslambdaric and its dependencies from the builder stage
COPY --chown=root:root --chmod=0755 --from=builder /build/ /var/task/

# Copy the Lambda Insights extension from the builder stage
COPY --chown=root:root --chmod=0755 --from=builder /opt/cloudwatch/ /opt/cloudwatch/

# Ensure /var/task is on the Python path so awslambdaric is importable
ENV PYTHONPATH=/var/task

# Switch to the non-root user (built into the base image)
USER nonroot

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "python", "-m", "awslambdaric" ]
