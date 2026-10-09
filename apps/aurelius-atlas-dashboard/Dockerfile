# syntax=docker/dockerfile:1

# The Apache Atlas dashboards, built unchanged from the Atlas 2.4.0 source tag (DD-001, DD-010).
# Atlas pins Node v12.16.0 for both dashboards (pom.xml: node-for-v2.version).
FROM node:12.16.0-buster AS build

ARG ATLAS_TAG=release-2.4.0
# The commit the tag pointed at when this file was written; the build fails if the tag moved.
ARG ATLAS_COMMIT=4787b753271718d0b06cf6545f331f9a12ce1f63

WORKDIR /src
RUN git clone --depth 1 --branch "${ATLAS_TAG}" https://github.com/apache/atlas.git . && \
    test "$(git rev-parse HEAD)" = "${ATLAS_COMMIT}"

# Same commands Atlas's Maven build runs (frontend-maven-plugin: npm install, grunt build-minify).
RUN cd dashboardv2 && npm install --no-audit --no-fund && npm run build-minify
RUN cd dashboardv3 && npm install --no-audit --no-fund && npm run build-minify

FROM dhi.io/nginx:1.30-alpine3.24

ARG VERSION=local

LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="The Apache Atlas dashboards served for Aurelius Atlas."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/aurelius-atlas
LABEL org.opencontainers.image.title="Aurelius Atlas Dashboard"
LABEL org.opencontainers.image.version="${VERSION}"

# dashboardv2 at /, dashboardv3 at /n/ — the paths Atlas 2.4.0 serves them on.
COPY --chown=root:root --chmod=0755 --from=build /src/dashboardv2/dist /usr/share/nginx/html
COPY --chown=root:root --chmod=0755 --from=build /src/dashboardv3/dist/n /usr/share/nginx/html/n
COPY --chown=root:root --chmod=0644 apps/aurelius-atlas-dashboard/nginx.conf /etc/nginx/conf.d/default.conf

USER nginx
EXPOSE 8080
