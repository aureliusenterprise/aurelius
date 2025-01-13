FROM httpd:2.4

LABEL org.opencontainers.image.source https://github.com/aureliusenterprise/aurelius

# Copy Atlas and Landing page
COPY dist/apps/atlas/browser/* backend/m4i-reverse-proxy/m4i_reverse_proxy/atlas/
COPY dist/apps/index-page/* backend/m4i-reverse-proxy/m4i_reverse_proxy/htdocs/

# Copy settings and configurations
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/* /usr/local/apache2/

COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf/httpd.conf /usr/local/apache2/conf/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf.d/ /usr/local/apache2/conf.d/

# Install dependencies and configure Apache
RUN apt-get update && \
    apt-get install -y curl jq ca-certificates libapache2-mod-auth-openidc && \
    ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/
