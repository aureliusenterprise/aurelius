# syntax=docker/dockerfile:1

# Use a hardened Python image with dev tools for the build stage.
FROM dhi.io/python:3.14-alpine3.24-dev AS build-image

# Set the working directory
WORKDIR /build

# Copy the wheel file into the container. Make sure the command points to the correct path.
COPY --chown=root:root --chmod=0755 apps/aurelius-fastapi-example/dist/*.whl .

# Install package dependencies, then clean up. Use a cache mount to speed up the process.
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --only-binary :all: --target=./ ./*.whl && \
    rm ./*.whl

# Use a hardened Python image for the final application image.
# Note: the hardened image does not include a shell or package manager.
FROM dhi.io/python:3.14-alpine3.24

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example FastAPI application."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius FastAPI Example"
LABEL org.opencontainers.image.version="${VERSION}"

# Set default values for the environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Set the working directory
WORKDIR /application

# Copy in the built dependencies
COPY --chown=root:root --chmod=0755 --from=build-image /build ./

# Switch to the non-root user (built into the base image)
USER nonroot

# Configure a healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os,urllib.request; p=os.getenv('PORT','8000'); urllib.request.urlopen('http://127.0.0.1:'+p+'/health/ready', timeout=5).close()"]

# Start the application
ENTRYPOINT [ "python", "-m", "aurelius_fastapi_example" ]
