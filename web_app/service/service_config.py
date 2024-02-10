import os
from dotenv import load_dotenv
load_dotenv()

# Redis Configuration
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
MARIADB_PORT = 3306

# HTTP Request Headers
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.google.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

TABLE_NAME = 'urls_table'
# Model and Tokenizer Configuration
TOKENIZER_CHECKPOINT = "/app/model/tokenizer/"
ONNX_MODEL_PATH = '/app/model/model.onnx'
ENCODER_PATH = '/app/model/encoder.pkl'