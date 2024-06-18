#!/bin/bash

# Add current directory as safe repository location
git config --global --add safe.directory $PWD

# Set node modules permissions
sudo chown -R $(whoami) /workspace/node_modules
sudo chmod -R 755 /workspace/node_modules

# Install dependencies
npm install
poetry install --no-root

# Download JAR files if not already present
JARS_DIR=/backend/m4i-flink-jobs/m4i_flink_jobs/jars/
if [ -d "$JARS_DIR" ]; then
    echo "Directory $DIRECTORY exists."
else
    wget -P "$JARS_DIR" "https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7/3.0.1-1.17/flink-sql-connector-elasticsearch7-3.0.1-1.17.jar"
    wget -P "$JARS_DIR" "https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.1/flink-sql-connector-kafka-1.17.1.jar"
fi

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
