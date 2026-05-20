#!/bin/bash

SEARCH_TOKEN=$(python ./backend/m4i-atlas-post-install/scripts/retrieve_elastic_search_key.py)
sed -i "s/appSearchToken: '.*'/appSearchToken: '$SEARCH_TOKEN'/g" ./apps/atlas/src/environments/environment.ts;
