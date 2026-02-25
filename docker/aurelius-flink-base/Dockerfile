ARG FLINK_VERSION=1.17.0

FROM flink:${FLINK_VERSION} AS builder

ARG PROJECT_DIR
ARG PYTHON_VERSION=3.8

# Set the working directory
WORKDIR /build

# Install Python 3.8. Use cache mounts to speed up subsequent builds.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    apt-get update && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends python${PYTHON_VERSION} python${PYTHON_VERSION}-distutils && \
    curl -sS https://bootstrap.pypa.io/pip/${PYTHON_VERSION}/get-pip.py | python${PYTHON_VERSION}

# Copy the jar files into the container
COPY ${PROJECT_DIR}/jars/*.jar ./jars/

# Copy the wheel file into the container
COPY ${PROJECT_DIR}/dist/*.whl ./

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --target=./ ./*.whl && \
    rm ./*.whl

FROM flink:${FLINK_VERSION} AS runtime

ARG PYTHON_MODULE_NAME
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
    curl -sS https://bootstrap.pypa.io/pip/${PYTHON_VERSION}/get-pip.py | python${PYTHON_VERSION}

# Set the working directory
WORKDIR /app

# Copy the installed Python packages and the main script from the builder stage
COPY --chown=flink:flink --chmod=0400 --from=builder /build/ ./

# Set environment variables
ENV JARS_ROOT=/app/jars
ENV PYFLINK_CLIENT_EXECUTABLE=/usr/bin/python${PYTHON_VERSION}
ENV PYTHON_MODULE_NAME=${PYTHON_MODULE_NAME}

# Command to run the application
CMD /opt/flink/bin/flink run -d -pym ${PYTHON_MODULE_NAME}
