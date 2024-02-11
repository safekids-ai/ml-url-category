#!/bin/sh

echo "Waiting for MariaDB to start..."
while ! mysqladmin ping -h"mariadb" --silent -u"root" -p"${MARIADB_ROOT_PASSWORD}"; do
    sleep 1
done

echo "Starting Service.."

exec uvicorn main:app --host 0.0.0.0 --port 8000