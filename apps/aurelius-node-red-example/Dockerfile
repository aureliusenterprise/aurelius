# syntax=docker/dockerfile:1

# Use the official Node.js LTS image as the base image
FROM node:lts AS builder

# Install required build dependencies, using cache mounts to speed up the process
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y python3

# Set the working directory
WORKDIR /build

# Copy settings file into the container
COPY apps/aurelius-node-red-example/settings.prod.js ./settings.js

# Copy application files into the container
COPY apps/aurelius-node-red-example/flows.json \
    apps/aurelius-node-red-example/package.json \
    ./

# Install Node-RED and dependencies, using a cache mount to speed up the process
RUN --mount=type=cache,mode=0755,target=/root/.npm \
    npm install

# Use the official Node.js LTS Alpine image as the runtime image
FROM node:lts-alpine AS runtime

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Node-RED application."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Node-RED Example"

# Expose the default Node-RED port
EXPOSE 1880

# Add a non-root user
RUN adduser --system aurelius

# Switch to the non-root user
USER aurelius

# Set the working directory
WORKDIR /app

# Copy the built application from the builder stage
COPY --chown=aurelius:aurelius --chmod=0755 --from=builder /build/ ./

# Configure a healthcheck to ensure the Node-RED flows have started
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD [ "sh", "-c", "wget -q -O - http://127.0.0.1:1880/flows/state | grep -q '\"state\":\"start\"' || exit 1" ]

# Run Node-RED
CMD [ "npx", "node-red", "-u", "/app" ]
