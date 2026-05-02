# syntax=docker/dockerfile:1

# Use a hardened base image with Node.js and build tools for the builder stage.
FROM dhi.io/node:24-alpine3.22-dev AS builder

# Install required build dependencies, using cache mounts to speed up the process
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache python3

# Set the working directory
WORKDIR /build

# Copy settings file into the container
COPY apps/aurelius-node-red-example/settings.prod.js ./settings.js

# Copy application files into the container
COPY apps/aurelius-node-red-example/package.json \
    apps/aurelius-node-red-example/flows.json \
    package-lock.json \
    ./

# Install Node-RED and dependencies, using a cache mount to speed up the process
RUN --mount=type=cache,mode=0755,target=/root/.npm \
    npm ci --ignore-scripts && \
    rm package-lock.json

# Use a hardened runtime image for the final image.
# Note that the runtime image does not include a shell or package manager.
FROM dhi.io/node:24-alpine3.22 AS runtime

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Node-RED application."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Node-RED Example"
LABEL org.opencontainers.image.version="${VERSION}"

# Expose the default Node-RED port
EXPOSE 1880

# Switch to the non-root user
USER node

# Set working directory to the copied application
WORKDIR /home/node/app

# Copy the built app from the builder stage
COPY --chown=root:root --chmod=0755 --from=builder /build/ ./

# Run the application
CMD [ "./node_modules/.bin/node-red", "-u", "/home/node/app" ]
