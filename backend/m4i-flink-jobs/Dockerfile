FROM flink:1.17.0 AS builder

LABEL org.opencontainers.image.source="https://github.com/aureliusenterprise/aurelius"

# Install Python 3.8
RUN apt-get update && \
  apt-get install -y --no-install-recommends software-properties-common && \
  apt-get update && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y --no-install-recommends python3.8 python3.8-distutils && \
  curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Create a symlink for `python` to `python3.8`
RUN ln -s /usr/bin/python3.8 /usr/bin/python

# Set the working directory
WORKDIR /tmp/build

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-flink-jobs/*.whl .

# Install the wheel file to a target directory
RUN pip install --no-cache-dir --target=/install *.whl && \
    rm -rf /tmp/build && \
    find /install -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type f -name "*.pyc" -delete && \
    find /install -type f -name "*.pyo" -delete

# Final stage
FROM flink:1.17.0

LABEL org.opencontainers.image.source="https://github.com/aureliusenterprise/aurelius"

# Install Python 3.8 (minimal install in final stage)
RUN apt-get update && \
  apt-get install -y --no-install-recommends software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y --no-install-recommends python3.8 python3.8-distutils && \
  curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create a symlink for `python` to `python3.8`
RUN ln -s /usr/bin/python3.8 /usr/bin/python

# Set the working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local/lib/python3.8/dist-packages

# Copy the main script into the container
COPY --chown=flink:flink --chmod=0400 backend/m4i-flink-jobs/main.py .

# Copy the jar files into the container
COPY --chown=flink:flink --chmod=0400 backend/m4i-flink-jobs/jars/*.jar ./jars/

# Switch to the non-root user
USER flink

# Command to run the application
CMD ["/opt/flink/bin/flink", "run", "-d", "-py", "main.py"]
