#!/usr/bin/env bash

set -e
upload_to_atlas () {
    echo "Uploading data to Apache Atlas..."
    ./upload_sample_data.sh
}

python init_app_search_engines.py
python init_atlas_types.py
if [[ "$UPLOAD_DATA" == "true" ]]
then
    upload_to_atlas
fi
pushd /opt/flink/py_libs/flink_jobs/
/opt/flink/bin/flink run -d --jobmanager "$JOBMANAGER_URL" -py synchronize_app_search.py
/opt/flink/bin/flink run -d --jobmanager "$JOBMANAGER_URL" -py publish_state.py
popd
if [[ "$UPLOAD_DATA" == "test-jobs" ]]
then
    upload_to_atlas
fi
