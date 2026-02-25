ARG JAVA_VERSION=8
ARG PYTHON_VERSION=3.9

# Build Apache Atlas from source
FROM eclipse-temurin:${JAVA_VERSION}-jdk-noble AS build

ARG PYTHON_VERSION

# Install required system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y g++ make maven python${PYTHON_VERSION}-venv

ENV PYTHON=python${PYTHON_VERSION}

# Install required Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python${PYTHON_VERSION} -m ensurepip && \
    python${PYTHON_VERSION} -m pip install --upgrade pip setuptools

WORKDIR /build

# Download Apache Atlas source code
COPY docker/apache-atlas/apache-atlas-sources.tar.gz ./

RUN tar -xzvf apache-atlas-sources.tar.gz

# Build Apache Atlas
WORKDIR /build/apache-atlas-sources

ENV MAVEN_OPTS="-Xms2g -Xmx2g"

RUN mvn clean install -DskipTests && \
    mvn clean -DskipTests package -Pdist,embedded-hbase-solr

# Extract the built Apache Atlas components
WORKDIR /atlas-bin

RUN tar xzf /build/apache-atlas-sources/distro/target/*bin.tar.gz --strip-components 1 -C ./

# Runtime image for Apache Atlas
FROM eclipse-temurin:${JAVA_VERSION}-jdk-noble AS runtime

ARG PYTHON_VERSION

# Add a non-root user for security
RUN groupadd -r atlas && useradd -r -g atlas atlas

# Install required system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python${PYTHON_VERSION}

# Switch to the non-root user
USER atlas

# Copy Apache Atlas files
WORKDIR /apache-atlas

COPY --chown=atlas:atlas --chmod=0777 --from=build /atlas-bin ./

# Create the data folder with appropriate permissions
RUN mkdir -p data && chown atlas:atlas data && chmod 700 data

# Set environment variables
ENV PATH=/apache-atlas/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Add healthcheck script
HEALTHCHECK --interval=30s --timeout=30s --start-period=180s --retries=3 CMD [ "sh", "-c", "curl -I -f -s http://localhost:21000 || exit 1" ]

# Start up Apache Atlas and keep the container running
CMD ["/bin/bash", "-c", "/apache-atlas/bin/atlas_start.py; tail -fF -n +1 /apache-atlas/logs/application.log"]
