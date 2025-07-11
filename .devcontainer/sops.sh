#!/bin/bash

# Generate a new secret key if one doesn't exist
if [ ! -f "$SOPS_AGE_KEY_FILE" ]; then
    nx keygen
fi
