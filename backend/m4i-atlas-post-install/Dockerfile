# Use the Flink image as the base
FROM flink:1.17.0

LABEL org.opencontainers.image.source https://github.com/aureliusenterprise/aurelius

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Install Python 3.8 and necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    apt-get update && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.8 python3.8-distutils curl && \
    curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 && \
    ln -s /usr/bin/python3.8 /usr/bin/python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-atlas-post-install/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Copy scripts and data into the container
COPY --chown=flink:flink --chmod=0550 backend/m4i-atlas-post-install/bin /app/bin
COPY --chown=flink:flink --chmod=0640 backend/m4i-atlas-post-install/data /app/data
COPY --chown=flink:flink --chmod=0440 backend/m4i-atlas-post-install/scripts /app/scripts

# Copy the main script into the container
COPY --chown=flink:flink --chmod=0400 backend/m4i-flink-jobs/main.py .
COPY --chown=flink:flink --chmod=0400 backend/m4i-flink-jobs/m4i_flink_jobs/*.py ./m4i_flink_jobs/
COPY --chown=flink:flink --chmod=0400 backend/m4i-flink-jobs/jars/*.jar ./jars/

# Switch to the Flink user
USER flink

# Run the main script
CMD ["/app/bin/run.sh"]
