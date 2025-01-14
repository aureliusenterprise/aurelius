FROM httpd:2.4

LABEL org.opencontainers.image.source="https://github.com/aureliusenterprise/aurelius"

# Copy Atlas and Landing page
COPY dist/apps/atlas/browser/ /usr/local/apache2/atlas/
COPY dist/apps/index-page/ /usr/local/apache2/htdocs/

# Copy settings and configurations
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf/httpd.conf /usr/local/apache2/conf/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf.d/ /usr/local/apache2/conf.d/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/init/ /usr/local/apache2/init/

# Install dependencies and configure Apache
RUN apt-get update && \
    apt-get install -y curl jq ca-certificates libapache2-mod-auth-openidc && \
    ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/
