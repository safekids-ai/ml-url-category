#!/bin/sh
# set -e

# Wait for MariaDB to start
echo "Waiting for MariaDB to start..."
while ! mysqladmin ping -h"db" -u"${MARIADB_USER}" -p"${MARIADB_PASSWORD}" --silent; do
    sleep 1
done

echo "Loading Data to MariaDB"

# Run your Python script
python load_data.py

# Exit the script
exit 0