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

# set permissions
sudo chmod -R 777 /opt/flink/log
sudo chown -R $(whoami) /opt/flink/log

# Prompt the user to set their git username and email if not already set
if [ -z "$(git config --global user.name)" ]; then
    read -p "Enter your Git username (full name): " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Enter your Git email: " git_email
    git config --global user.email "$git_email"
fi
