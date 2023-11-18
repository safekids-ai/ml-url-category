import json
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # This loads the environment variables from .env

MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')

conn = mysql.connector.connect(
    host='db',
    port = 3306,
    user = MARIADB_USER,
    password = MARIADB_PASSWORD,
    database = MARIADB_DATABASE 
)
cursor = conn.cursor()
table_name = 'urls_table'

sql = f"SHOW TABLES LIKE '{table_name}'"
cursor.execute(sql)
table_exists = cursor.fetchone() is not None


def main():
    if not table_exists:
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT,
            url VARCHAR(255),
            meta VARCHAR(255),
            prediction VARCHAR(255),
            PRIMARY KEY (id));"""
        )


        # Open and read the JSON file
        with open('predicted_labels.json') as file:
            data = json.load(file)

            # Assuming data is a list of dicts
            for entry in data:
                # Change 'id' and 'label' according to your JSON structure
                url = entry['url']
                meta = entry['meta']
                prediction = entry['prediction']
                cursor.execute(f"INSERT INTO {table_name} (url,meta,prediction) VALUES (%s, %s, %s)", (url,meta,prediction))

        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
