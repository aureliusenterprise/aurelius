#!/usr/bin/env bash

set -e

python /app/scripts/init_app_search_engines.py
python /app/scripts/init_atlas_types.py

cd /app/bin/

if [[ "$UPLOAD_DATA" == "true" ]]
then
    echo "Uploading full dataset to Apache Atlas..."
    bash /app/bin/upload_sample_data.sh
else
    echo "Uploading governance quality rules to Apache Atlas..."
    bash /app/bin/upload_sample_data.sh only_gov_quality.zip
fi
