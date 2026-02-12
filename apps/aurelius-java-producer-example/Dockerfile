# Use the Eclipse Temurin JRE base image for Java 21 as the builder stage
FROM eclipse-temurin:21.0.9_10-jre-alpine-3.23 AS builder

# Set the working directory
WORKDIR /build

# Copy the built application tarball from the host
COPY --chown=root:root --chmod=0755 apps/aurelius-java-producer-example/build/distributions/aurelius-java-producer-example.tar ./

# Extract the application files from the tarball and remove the tarball
RUN tar -xvf aurelius-java-producer-example.tar --strip-components=1 && rm aurelius-java-producer-example.tar

# Use the Eclipse Temurin JRE base image for Java 21 as the runtime stage
FROM eclipse-temurin:21.0.9_10-jre-alpine-3.23 AS runtime

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example Kafka producer written in Java."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Java Producer Example"

# Add a non-root user to run the application
RUN adduser -S aurelius

# Switch to the non-root user
USER aurelius

# Set the working directory
WORKDIR /app

# Copy the application files from the builder stage to the runtime stage
COPY --chown=root:root --chmod=0755 --from=builder /build/ ./

# Run the application
CMD ["./bin/aurelius-java-producer-example"]
