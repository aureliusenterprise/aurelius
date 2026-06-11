#!/bin/bash
if [[ -v NAMESPACE ]]; then
    mv /usr/local/apache2/htdocs/index.html /usr/local/apache2/htdocs/index.orig.html
    sed "s/<base href=\"\//<base href=\"\/$NAMESPACE\//g" /usr/local/apache2/htdocs/index.orig.html > /usr/local/apache2/htdocs/index.html

    mv /usr/local/apache2/atlas/index.html /usr/local/apache2/atlas/index.orig.html
    sed "s/<base href=\"\//<base href=\"\/$NAMESPACE\/atlas\//g" /usr/local/apache2/atlas/index.orig.html > /usr/local/apache2/atlas/index.html

    sed -i "s/url:\"\/auth\"/url:\"\/$NAMESPACE\/auth\"/g" /usr/local/apache2/atlas/main*.js

    mkdir /usr/local/apache2/bak2/
    cp /usr/local/apache2/htdocs/main*.js /usr/local/apache2/bak2/
    sed -i "s/url:\"\/auth\"/url:\"\/$NAMESPACE\/auth\"/g" /usr/local/apache2/htdocs/main*.js
fi
