#!/bin/bash

# Get the CODIO_HOSTNAME environment variable
HOSTNAME=${CODIO_HOSTNAME}

# Construct the URL
URL="https://${HOSTNAME}-5000.codio.io"

# Open the URL in a new tab or window (using xdg-open or similar)
# Since we're in Codio, we might not have xdg-open, so let's just echo the URL
echo "Opening $URL"
echo "$URL"