#!/bin/bash

# Add current directory as safe repository location
git config --global --add safe.directory $PWD

# Install dependencies
npm install
poetry install

JARS_DIR=backend/m4i-flink-jobs/m4i_flink_jobs/jars

# Download JAR files if not already present
while read -r url; do
    [ -z "$url" ] && continue
    filename=$(basename "$url")
    if [ -e "$JARS_DIR/$filename" ]; then
        echo "File jars/$filename already exists, skipping download."
        continue
    fi

    wget -P "$JARS_DIR/" "$url"
done < "$JARS_DIR/manifest"

####################
# Atlas Post Install
####################
upload_to_atlas () {
    echo "Uploading data to Apache Atlas..."
    ./upload_sample_data.sh
}

# Set flink log permission
sudo chmod -R 777 /opt/flink/log
sudo chown -R $(whoami) /opt/flink/log
# Init dependencies
cd backend/m4i-atlas-post-install/scripts
pip install elastic_enterprise_search elasticsearch dictdiffer urlpath

# Init Elastic and Atlas
python init_app_search_engines.py
python init_atlas_types.py

if [[ "$UPLOAD_DATA" == "true" ]]
then
    upload_to_atlas
fi

# Start jobs
pushd /workspace/backend/m4i-flink-jobs/m4i_flink_jobs/
/opt/flink/bin/flink run -d -py synchronize_app_search.py
/opt/flink/bin/flink run -d -py publish_state.py
popd

if [[ "$UPLOAD_DATA" == "test-jobs" ]]
then
    upload_to_atlas
fi

# Set elasticsearch token in enviroment.ts of the Angular app
echo "Setting appSearchToken in Atlas"
export SEARCH_TOKEN=$(python retrieve_elastic_search_key.py)
sed -i "s/appSearchToken: '.*'/appSearchToken: '$SEARCH_TOKEN'/g" /workspace/apps/atlas/src/environments/environment.ts;

# Prompt the user to set their git username and email if not already set
if [ -z "$(git config --global user.name)" ]; then
    read -p "Enter your Git username (full name): " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Enter your Git email: " git_email
    git config --global user.email "$git_email"
fi
