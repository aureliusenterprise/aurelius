#!/bin/bash

# Start the main service
/etc/confluent/docker/run 2>&1 &

# Run the init script
/tmp/aurelius/bin/init.sh 2>&1

# Keep the container running
tail -f /dev/null
