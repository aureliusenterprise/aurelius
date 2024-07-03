# Use the official Python image as a base
FROM python:3.8-slim

# Create a non-root user and group
RUN addgroup --system m4i-atlas-post-install && \
    adduser --system --ingroup m4i-atlas-post-install m4i-atlas-post-install

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-atlas-post-install/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Copy scripts and data into the container
COPY --chown=m4i-atlas-post-install:m4i-atlas-post-install --chmod=0550 backend/m4i-atlas-post-install/bin /app/bin
COPY --chown=m4i-atlas-post-install:m4i-atlas-post-install --chmod=0440 backend/m4i-atlas-post-install/data /app/data
COPY --chown=m4i-atlas-post-install:m4i-atlas-post-install --chmod=0440 backend/m4i-atlas-post-install/scripts /app/scripts

# Switch to the non-root user
USER m4i-atlas-post-install

# Run the main script
CMD ["./bin/run.sh"]
