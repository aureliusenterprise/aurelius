# Use the official Python image as the base
FROM python:3.8

LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius

# Install dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends curl

# Set the working directory
WORKDIR /app

# Copy the scripts and data into the container
COPY --chown=root:root --chmod=0550 backend/m4i-atlas-post-install/bin ./bin
COPY --chown=root:root --chmod=0440 backend/m4i-atlas-post-install/scripts ./scripts
COPY --chown=root:root --chmod=0640 backend/m4i-atlas-post-install/data ./data

# Copy the wheel file into the container
COPY --chown=root:root --chmod=0755 backend/m4i-atlas-post-install/dist/*.whl ./

# Install the wheel file
RUN  --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install ./*.whl

# Run the main script
CMD ["/app/bin/run.sh"]
