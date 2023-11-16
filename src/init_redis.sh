#!/bin/bash

# Wait for MariaDB to be ready (adjust the host and port as needed)
until nc -z -v -w30 mariadb 3306; do
  echo "Waiting for MariaDB to start..."
  sleep 1
done

# Fetch data from MariaDB and store it in Redis
python fetch_data_from_mariadb.py

# Start the Redis server
exec docker-entrypoint.sh redis-server
