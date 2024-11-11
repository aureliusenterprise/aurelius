FROM httpd:2.4
LABEL maintainer="andreas.wombacher@aureliusenterprise.com"

COPY dist/apps/atlas/browser/* backend/m4i-reverse-proxy/m4i_reverse_proxy/atlas/
COPY dist/apps/atlas/3rdpartylicenses.txt backend/m4i-reverse-proxy/m4i_reverse_proxy/atlas/

COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/htdocs/ /usr/local/apache2/htdocs/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/atlas/ /usr/local/apache2/atlas/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/init/ /usr/local/apache2/init/
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY backend/m4i-reverse-proxy/m4i_reverse_proxy/conf.d/ /usr/local/apache2/conf.d/

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y jq && \
    apt-get install -y ca-certificates && \
    apt-get install -y libapache2-mod-auth-openidc && \
    ln -s /usr/lib/apache2/modules/mod_auth_openidc.so /usr/local/apache2/modules/ # module gets installed in /usr/lib, but is required in /usr/local
