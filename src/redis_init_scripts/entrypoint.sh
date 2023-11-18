#!/bin/bash
# custom_entrypoint.sh

# Wait for MariaDB to start
echo "Waiting for MariaDB to start..."
while ! mysqladmin ping -h"db" -u"${MARIADB_USER}" -p"${MARIADB_PASSWORD}" --silent; do
    sleep 1
done

echo "Waiting for loading data in MariaDB..."
while [ ! -f /var/shared/done.txt ]; do
  sleep 1
done

rm -f /var/shared/done.txt

# Wait for Redis to start
echo "Waiting for Redis to start..."
while ! redis-cli -h redis -p 6379 ping -a${REDIS_PASSWORD}; do
    sleep 1
done

echo "Populating redis..."

# tail -f /dev/null
# Run the data fetching and populating script
python3 fetch_and_populate.py

echo "Populated"

exit 0