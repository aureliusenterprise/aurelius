# syntax=docker/dockerfile:1

# Use a hardened Python image with dev tools for the build stage.
FROM dhi.io/python:3.14-alpine3.24-dev AS build-image

WORKDIR /build

# The wheel (with its workspace dependencies bundled) comes from `nx build aurelius-atlas-server`.
COPY --chown=root:root --chmod=0755 apps/aurelius-atlas-server/dist/*.whl .

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --only-binary :all: --target=./ ./*.whl && \
    rm ./*.whl

# Use a hardened Python image for the final application image (no shell, no package manager).
FROM dhi.io/python:3.14-alpine3.24

ARG VERSION=local

LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="Aurelius Atlas server: the Apache Atlas REST API on Elasticsearch 9."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius-atlas
LABEL org.opencontainers.image.title="Aurelius Atlas Server"
LABEL org.opencontainers.image.version="${VERSION}"

ENV AURELIUS_ATLAS_SERVER_HOST=0.0.0.0
ENV AURELIUS_ATLAS_SERVER_PORT=21000
ENV AURELIUS_ATLAS_SERVER_BUILD_REVISION=${VERSION}

WORKDIR /application
COPY --chown=root:root --chmod=0755 --from=build-image /build ./

USER nonroot

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:21000/api/atlas/admin/liveness', timeout=5).close()"]

EXPOSE 21000
ENTRYPOINT [ "python", "-m", "aurelius_atlas_server" ]
