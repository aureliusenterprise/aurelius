# syntax=docker/dockerfile:1

# Use the official Python image as a base image for building the application
FROM python:3.8 AS build-image

# Set the working directory
WORKDIR /build

# Copy the wheel file into the container. Make sure the command points to the correct path.
COPY --chown=root:root --chmod=0755 apps/m4i-data-dictionary-io/dist/*.whl .

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --target=./ ./*.whl && \
    rm ./*.whl

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.8-slim

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This application indexes a configured data source and adds corresponding entities into Aurelius Atlas."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius
LABEL org.opencontainers.image.title="M4I Data Dictionary IO"

# Create a non-root user and group
RUN addgroup --system m4i-data-dictionary-io && \
    adduser --system --ingroup m4i-data-dictionary-io m4i-data-dictionary-io

# Set the working directory
WORKDIR /app

# Copy in the built dependencies
COPY --chown=root:root --chmod=0755 --from=build-image /build ./

# Switch to the non-root user
USER m4i-data-dictionary-io

# Run the main script
CMD ["python", "-m", "m4i_data_dictionary_io"]
