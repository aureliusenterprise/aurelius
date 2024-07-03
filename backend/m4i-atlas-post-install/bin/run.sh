#!/usr/bin/env bash

set -e

python /app/scripts/init_app_search_engines.py
python /app/scripts/init_atlas_types.py

if [[ "$UPLOAD_DATA" == "true" ]]
then
    echo "Uploading data to Apache Atlas..."
    bash /app/bin/upload_sample_data.sh
fi
