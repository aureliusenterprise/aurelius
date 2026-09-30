# syntax=docker/dockerfile:1
# Reverse proxy of Aurelius on pyatlas with the Angular frontend (apps/atlas) built from this repository.
# Build context = repository root:  docker build -f docker/aurelius-reverse-proxy/Dockerfile .
FROM node:20-bookworm-slim AS frontend
WORKDIR /src
ENV CYPRESS_INSTALL_BINARY=0 PUPPETEER_SKIP_DOWNLOAD=1 NX_DAEMON=false NX_NO_CLOUD=true
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund --loglevel=error --ignore-scripts
COPY nx.json tsconfig.base.json jest.preset.js jest.config.ts git-version.js git-version.json .eslintrc.json .eslintignore .nxignore .prettierrc ./
COPY tools ./tools
COPY libs ./libs
COPY apps/atlas ./apps/atlas
# no namespace in the build: the page finds its base URL (/<namespace>/<tenant>/atlas/) itself and gets the
# Keycloak URL and realm from config.json (pyatlas), so one image serves any namespace (AURELIUS_NS at run time)
RUN npx nx build atlas --configuration=production --skip-nx-cache \
 && grep -q "setAttribute('href'" dist/apps/atlas/browser/index.html

FROM httpd:2.4
# OpenID Connect for the admin tools (Kibana), as in backend/m4i-reverse-proxy
RUN apt-get update \
 && apt-get install -y --no-install-recommends libapache2-mod-auth-openidc ca-certificates \
 && ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/mod_auth_openidc.so \
 && rm -rf /var/lib/apt/lists/*
COPY --from=frontend /src/dist/apps/atlas/browser/ /usr/local/apache2/atlas/
COPY docker/aurelius-reverse-proxy/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY docker/aurelius-reverse-proxy/aurelius.conf docker/aurelius-reverse-proxy/kibana-tenants.conf /usr/local/apache2/conf.d/
RUN mkdir -p /usr/local/apache2/tenants/oidc \
 && echo "# tenant  Kibana API key (written by aurelius-admin)" > /usr/local/apache2/tenants/kibana-keys.txt
# AURELIUS_NS: first path segment of every URL (the Helm chart sets the Kubernetes namespace)
# TENANTS_DIR: files of aurelius-admin (the realms as Kibana login providers, the tenants' Kibana keys)
ENV PYATLAS_URL=http://pyatlas:21000 KEYCLOAK_URL=http://keycloak:8080 KIBANA_URL=http://kibana:5601 \
    PUBLIC_URL=http://localhost:9090 DEFAULT_TENANT=m4i TENANTS_DIR=/usr/local/apache2/tenants \
    AURELIUS_NS=aurelius
# PROXY_CRYPTO_PASSPHRASE has no default: it must be passed (docker-compose, .env)
EXPOSE 8080
