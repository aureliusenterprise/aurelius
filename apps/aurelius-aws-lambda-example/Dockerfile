# syntax=docker/dockerfile:1

# Use the official Python image as a base image for building the application
FROM python:3.14 AS build-image

# Set the working directory
WORKDIR /build

# Copy the wheel file into the container. Make sure the command points to the correct path.
COPY --chown=root:root --chmod=0755 apps/aurelius-aws-lambda-example/dist/*.whl ./

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --target=./ ./*.whl && \
    rm ./*.whl

# Use the AWS Lambda base image for the final image
FROM ghcr.io/aureliusenterprise/aurelius-aws-lambda-base:latest

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example AWS lambda function."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius AWS Lambda Example"

# Copy in the built dependencies
COPY --chown=root:root --chmod=0755 --from=build-image /build ./

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "aurelius_aws_lambda_example.main" ]
