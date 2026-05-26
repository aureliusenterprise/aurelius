#!/bin/bash

# Add current directory as safe repository location
git config --global --add safe.directory $PWD

# Install pre-commit hooks
poetry run pre-commit install
