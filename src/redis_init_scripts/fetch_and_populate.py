import mysql.connector
import redis
import time
import os
import json
from dotenv import load_dotenv

load_dotenv() 

MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')


table_name = 'urls_table'

conn = mysql.connector.connect(
    host='db',
    port = 3306,
    user = MARIADB_USER,
    password = MARIADB_PASSWORD,
    database = MARIADB_DATABASE 
)


def main():
    r = redis.Redis(host='redis', port=6379, decode_responses=True, password=REDIS_PASSWORD)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    
    column_names = [desc[0] for desc in cursor.description]

    # Iterate over rows to store them in Redis
    for row in rows:
        redis_key = row[1]  # Assuming 'url' is the second column
        redis_value = {column_names[i]: row[i] for i in range(len(row))}

        # Convert the value dictionary to a JSON string
        value_json = json.dumps(redis_value)

        # Store in Redis
        r.set(redis_key, value_json)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()





