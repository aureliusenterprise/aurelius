#!/bin/bash

# Add current directory as safe repository location
git config --global --add safe.directory $PWD

# Install dependencies
npm install
poetry install
