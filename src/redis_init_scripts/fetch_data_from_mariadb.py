import mysql.connector
import redis
import time

def wait_for_mariadb():
    connected = False
    while not connected:
        try:
            db = mysql.connector.connect(
                host="mariadb",
                user="your_username",
                password="your_password",
                database="your_database_name"
            )
            connected = True
        except mysql.connector.Error as err:
            print("Waiting for MariaDB...")
            time.sleep(2)
    return db

def wait_for_redis():
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    while True:
        try:
            r.ping()
            return r
        except redis.exceptions.ConnectionError:
            print("Waiting for Redis...")
            time.sleep(2)

def main():
    db = wait_for_mariadb()
    r = wait_for_redis()
    cursor = db.cursor()

    # Fetch data from MariaDB
    cursor.execute("SELECT * FROM your_table")
    rows = cursor.fetchall()

    # Populate Redis with the data
    for row in rows:
        r.set(row[0], row[1])  # Assuming row[0] is the key and row[1] is the value

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
