#!/bin/sh

# Wait for MariaDB to be ready
echo "Waiting for MariaDB to start..."
while ! mysqladmin ping -h"mariadb" --silent -u"root" -p"${MARIADB_ROOT_PASSWORD}"; do
    sleep 1
done


echo "Preparing database and table..."
mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} -e "
CREATE DATABASE IF NOT EXISTS safekids_db;
USE safekids_db;

CREATE TABLE IF NOT EXISTS urls_table (
    id INT AUTO_INCREMENT,
    url VARCHAR(255) NOT NULL,
    label INT,
    probability FLOAT,
    PRIMARY KEY (id)
);
"
ROW_COUNT=$(mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} -e "
SELECT COUNT(*) FROM safekids_db.urls_table;
" | tail -n 1)

if [ "$ROW_COUNT" -eq 0 ]; then
    echo "Importing CSV data..."
    mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
    LOAD DATA LOCAL INFILE '/usr/local/bin/data/mariadb_data.csv'
    INTO TABLE urls_table
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '\"'
    LINES TERMINATED BY '\n'
    (url, label, probability);
    "
else
    echo "Table already has data, skipping CSV import."
fi

# # Import CSV data into MariaDB
# echo "Importing CSV data..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
# LOAD DATA LOCAL INFILE '/usr/local/bin/data/mariadb_data.csv'
# INTO TABLE urls_table
# FIELDS TERMINATED BY ','
# OPTIONALLY ENCLOSED BY '\"'
# LINES TERMINATED BY '\n'
# (url, label, probability);
# "

# echo "Creating temporary table..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
# CREATE TABLE IF NOT EXISTS temp_urls_table LIKE urls_table;
# "

# echo "Importing CSV data into temporary table..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
# LOAD DATA LOCAL INFILE '/usr/local/bin/data/mariadb_data.csv'
# INTO TABLE temp_urls_table
# FIELDS TERMINATED BY ','
# OPTIONALLY ENCLOSED BY '\"'
# LINES TERMINATED BY '\n'
# (url, label, probability);
# "



# echo "Inserting new data into main table..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
# INSERT INTO urls_table (url, label, probability)
# SELECT t.url, t.label, t.probability
# FROM temp_urls_table t
# LEFT JOIN urls_table u ON t.url = u.url
# WHERE u.url IS NULL;
# "

# echo "Cleaning up temporary table..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "DROP TABLE IF EXISTS temp_urls_table;"


echo "Data import complete."


# # Import CSV data into MariaDB
# echo "Importing CSV data..."
# mysql -h mariadb -uroot -p${MARIADB_ROOT_PASSWORD} ${MARIADB_DATABASE} -e "
# LOAD DATA LOCAL INFILE '/usr/local/bin/data/mariadb_data.csv'
# INTO TABLE urls_table
# FIELDS TERMINATED BY ','
# OPTIONALLY ENCLOSED BY '\"'
# LINES TERMINATED BY '\n'
# (url, label, probability);
# "

# echo "pwd"
# pwd

# echo "ls"
# ls usr/local/bin/data/
