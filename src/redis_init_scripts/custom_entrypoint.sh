#!/bin/bash
# custom_entrypoint.sh

# Run the data fetching and populating script
python3 /usr/local/bin/fetch_and_populate.py

# Call the original Redis entrypoint
exec docker-entrypoint.sh redis-server "$@"
