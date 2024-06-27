#!/bin/bash

# Add current directory as safe repository location
git config --global --add safe.directory $PWD

# Install dependencies
npm install
poetry install --no-root

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
# Set flink log permission
sudo chmod -R 777 /opt/flink/log
sudo chown -R $(whoami) /opt/flink/log
# Init dependencies
cd backend/m4i-atlas-post-install/m4i_atlas_post_install
pip install elastic_enterprise_search elasticsearch dictdiffer urlpath
# Init Elastic and Atlas
python init_app_search_engines.py
python init_atlas_types.py
# Start jobs
pushd /workspace/backend/m4i-flink-jobs/m4i_flink_jobs/
/opt/flink/bin/flink run -d -py synchronize_app_search.py
/opt/flink/bin/flink run -d -py publish_state.py
popd

./upload_sample_data

# Prompt the user to set their git username and email if not already set
if [ -z "$(git config --global user.name)" ]; then
    read -p "Enter your Git username (full name): " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Enter your Git email: " git_email
    git config --global user.email "$git_email"
fi
