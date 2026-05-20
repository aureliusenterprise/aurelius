# syntax=docker/dockerfile:1

# Set global build arguments
ARG FLINK_VERSION=1.17.0

# Use the official Flink image as the base image
FROM flink:${FLINK_VERSION}

# Set build arguments
ARG PYTHON_VERSION=3.8

# Install Python 3.8. Use cache mounts to speed up the process.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && \
  apt-get install -y --no-install-recommends software-properties-common && \
  apt-get update && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y --no-install-recommends python${PYTHON_VERSION} python${PYTHON_VERSION}-distutils && \
  curl -sS https://bootstrap.pypa.io/pip/${PYTHON_VERSION}/get-pip.py | python${PYTHON_VERSION} && \
  ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# Set the working directory
WORKDIR /app

# Set environment variables
ENV JARS_ROOT=/app/jars/

# Copy the jar files into the container
COPY --chown=flink:flink --chmod=0500 backend/m4i-publish-state/jars/*.jar ${JARS_ROOT}

# Copy the wheel file into the container
COPY --chown=flink:flink --chmod=0400 backend/m4i-publish-state/dist/*.whl ./

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
  python -m pip install --upgrade --force-reinstall --ignore-installed ./*.whl
