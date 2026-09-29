# syntax=docker/dockerfile:1
# Reverse proxy of Aurelius on pyatlas with the Angular frontend (apps/atlas) built from this repository.
# Build context = repository root:  docker build -f dev/pyatlas/reverse-proxy/Dockerfile .
ARG NAMESPACE=aurelius

FROM node:20-bookworm-slim AS frontend
ARG NAMESPACE
WORKDIR /src
ENV CYPRESS_INSTALL_BINARY=0 PUPPETEER_SKIP_DOWNLOAD=1 NX_DAEMON=false NX_NO_CLOUD=true
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund --loglevel=error --ignore-scripts
COPY nx.json tsconfig.base.json jest.preset.js jest.config.ts git-version.js git-version.json .eslintrc.json .eslintignore .nxignore .prettierrc ./
COPY tools ./tools
COPY libs ./libs
COPY apps/atlas ./apps/atlas
RUN npx nx build atlas --configuration=production --skip-nx-cache \
 && cd dist/apps/atlas/browser \
 && sed -i "s#<base href=\"/\">#<base href=\"/${NAMESPACE}/atlas/\">#" index.html \
 && sed -i "s#url:\"/auth\"#url:\"/${NAMESPACE}/auth\"#" main-*.js \
 && grep -q "/${NAMESPACE}/atlas/" index.html && grep -q "/${NAMESPACE}/auth" main-*.js

FROM httpd:2.4
ARG NAMESPACE
# OpenID Connect for the admin tools (Kibana), as in backend/m4i-reverse-proxy
RUN apt-get update \
 && apt-get install -y --no-install-recommends libapache2-mod-auth-openidc ca-certificates \
 && ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/mod_auth_openidc.so \
 && rm -rf /var/lib/apt/lists/*
COPY --from=frontend /src/dist/apps/atlas/browser/ /usr/local/apache2/atlas/
COPY dev/pyatlas/reverse-proxy/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY dev/pyatlas/reverse-proxy/aurelius.conf /usr/local/apache2/conf.d/aurelius.conf
RUN sed -i "s#^Define NS .*#Define NS ${NAMESPACE}#" /usr/local/apache2/conf.d/aurelius.conf
ENV PYATLAS_URL=http://pyatlas:21000 KEYCLOAK_URL=http://keycloak:8080 KIBANA_URL=http://kibana:5601 \
    PUBLIC_URL=http://localhost:9090 REALM=m4i PROXY_CLIENT_ID=aurelius_proxy
# PROXY_CLIENT_SECRET and PROXY_CRYPTO_PASSPHRASE have no defaults: they must be passed (docker-compose, .env)
EXPOSE 8080
