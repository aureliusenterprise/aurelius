# Use a hardened base image with Java 21 and Alpine Linux for the build stage
FROM dhi.io/eclipse-temurin:21-alpine3.22-dev AS builder

# Set the working directory
WORKDIR /build

# Copy the built application tarball from the host
COPY --chown=root:root --chmod=0755 apps/aurelius-java-producer-example/build/distributions/aurelius-java-producer-example.tar ./

# Extract the application files from the tarball and remove the tarball
RUN tar -xvf aurelius-java-producer-example.tar --strip-components=1 && rm aurelius-java-producer-example.tar

# Use a hardened base image with Java 21 and Alpine Linux for the runtime stage
# Note: the hardened image does not have a shell or package manager
FROM dhi.io/eclipse-temurin:21-alpine3.22 AS runtime

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Kafka producer written in Java."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Java Producer Example"
LABEL org.opencontainers.image.version="${VERSION}"

# Set the working directory
WORKDIR /app

# Copy the application files from the builder stage to the runtime stage
COPY --chown=root:root --chmod=0755 --from=builder /build/ ./

# Switch to the non-root user
USER nonroot

# Run the application
CMD ["java", "-cp", "lib/*", "com.aureliusenterprise.producer.App"]
