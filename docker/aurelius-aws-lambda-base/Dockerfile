# syntax=docker/dockerfile:1

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.14-slim

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is a base image for AWS Lambda functions."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius AWS Lambda Base"
LABEL org.opencontainers.image.version="${VERSION}"

# Add a non-root user and group
RUN addgroup --system aurelius-aws-lambda && \
    adduser --system --ingroup aurelius-aws-lambda aurelius-aws-lambda

# Install required system dependencies and the AWS Lambda Insights extension
# Tools that are only needed for installation are removed afterwards to reduce image size
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y alien curl && \
    curl -O https://lambda-insights-extension.s3-ap-northeast-1.amazonaws.com/amazon_linux/lambda-insights-extension.rpm && \
    alien -i lambda-insights-extension.rpm && \
    rm -f lambda-insights-extension.rpm && \
    apt-get remove -y alien curl && \
    apt-get autoremove -y

# Install AWS Lambda dependencies for Python. Use a cache mount to speed up the process
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --only-binary=:all: awslambdaric==4.0.0

# Set the working directory
WORKDIR /var/task

# Switch to the non-root user
USER aurelius-aws-lambda

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "python", "-m", "awslambdaric" ]
