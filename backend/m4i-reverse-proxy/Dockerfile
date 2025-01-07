FROM httpd:2.4
LABEL maintainer="andreas.wombacher@aureliusenterprise.com"

# Copy Atlas and Landing page
COPY dist/apps/atlas/browser/* dist/apps/atlas/3rdpartylicenses.txt backend/m4i-reverse-proxy/m4i_reverse-proxy/atlas/
COPY dist/apps/index-page/* backend/m4i-reverse-proxy/m4i_reverse-proxy/htdocs/

# Copy settings and configurations
COPY backend/m4i-reverse-proxy/m4i_reverse-proxy/{htdocs,atlas,init} /usr/local/apache2/
COPY backend/m4i-reverse-proxy/m4i_reverse-proxy/conf/httpd.conf /usr/local/apache2/conf/
COPY backend/m4i-reverse-proxy/m4i_reverse-proxy/conf.d/ /usr/local/apache2/conf.d/

# Install dependencies and configure Apache
RUN apt-get update && \
    apt-get install -y curl jq ca-certificates libapache2-mod-auth-openidc && \
    ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/
