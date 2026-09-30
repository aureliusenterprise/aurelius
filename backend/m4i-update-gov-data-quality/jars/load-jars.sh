#!/bin/bash

# Define the directory where JAR files will be stored
JARS_DIR=$(dirname "$0")

# Check if JARS_DIR exists
if [ ! -d "$JARS_DIR" ]; then
    echo "Directory $JARS_DIR does not exist. Creating it now."
    mkdir -p "$JARS_DIR"
fi

# Check if manifest file exists
if [ ! -f "$JARS_DIR/manifest" ]; then
    echo "Manifest file not found in $JARS_DIR. Exiting."
    exit 1
fi

# Download JAR files if not already present
while IFS= read -r url; do
    [ -z "$url" ] && continue
    filename=$(basename "$url")
    if [ -e "$JARS_DIR/$filename" ]; then
        echo "File $JARS_DIR/$filename already exists, skipping download."
        continue
    fi

    echo "Downloading $filename from $url..."
    if wget -P "$JARS_DIR/" "$url"; then
        echo "Downloaded $filename successfully."
    else
        echo "Failed to download $filename from $url."
    fi
done < "$JARS_DIR/manifest"
