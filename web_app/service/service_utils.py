import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pickle
import onnxruntime
import numpy as np
from transformers import AutoTokenizer
import redis
from bs4.element import Comment
import mysql.connector
import re

from service_config import REDIS_PASSWORD, HEADERS, TOKENIZER_CHECKPOINT, ONNX_MODEL_PATH, ENCODER_PATH, TABLE_NAME

from service_config import MARIADB_USER, MARIADB_PASSWORD, MARIADB_DATABASE, MARIADB_PORT

# Initialize Redis connection
def init_redis():
    return redis.Redis(host='redis', port=6379, decode_responses=True, password=REDIS_PASSWORD)

def init_mariadb():
    return mysql.connector.connect(
    host='mariadb',
    port = MARIADB_PORT,
    user = MARIADB_USER,
    password = MARIADB_PASSWORD,
    database = MARIADB_DATABASE 
)
 
# Load ONNX model
def load_model():
    providers = onnxruntime.get_available_providers()
    if 'CUDAExecutionProvider' in providers:
        return onnxruntime.InferenceSession(ONNX_MODEL_PATH, providers=['CUDAExecutionProvider'])
    else:
        return onnxruntime.InferenceSession(ONNX_MODEL_PATH, providers=['CPUExecutionProvider'])


# Load tokenizer and encoder
def load_tokenizer_and_encoder():
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_CHECKPOINT)
    with open(ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)
    return tokenizer, encoder


# Check cache for a given URL
def check_cache(redis_conn, url):
    return redis_conn.get(url)


def retrieve_from_web(url,tokenizer,session,encoder):
    text = retrieve_text(url)
    inputs = tokenizer(text, return_tensors="np", max_length=512, truncation=True, padding=True)
    onnx_inputs = {k: v for k, v in inputs.items() if k in [i.name for i in session.get_inputs()]}
    outputs = session.run(None, onnx_inputs)[0]
    probabilities = np.exp(outputs) / np.sum(np.exp(outputs), axis=1, keepdims=True)
    probability = np.max(probabilities)
    if probability < 0.7:
        pred_class = encoder.transform(['safe'])[0]
        probability = 0.7
    else:
        pred_class = np.argmax(probabilities, axis=1)[0]
    return int(pred_class), float(probability)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def remove_www_http_https(url):
    return re.sub(r'^(https?://)?(www\.)?', '', url, flags=re.IGNORECASE)

def filter_meta(meta):
    filtered=[]
    for m in meta:
        cond1 = any(type(v)==str for v in m.values())
        if m['name']==None:
            m['name']=''
        if m['content']==None:
            m['content']=''
        if cond1:
            conds=[]
            conds.append(not m['content'].isnumeric())
            conds.append(' ' in m['content'])
            conds.append(not any([k in m['name'] for k in ['viewport','twitter','robots','generator']]))
            conds.append(not any([k in m['content'] for k in ['text/html','charset','UTF-8']]))
            if all(conds):
                filtered.append(m)
    return list({i['content']:i for i in reversed(filtered)}.values())

# Retrieve text from URL
def retrieve_text(url):
    if not urlparse(url).scheme:
        url = "http://" + url
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else ''
        meta_tags = [{'name': tag.get('name'), 'content': tag.get('content')} for tag in soup.find_all('meta')]
        meta_tags = filter_meta(meta_tags)[:100]
        meta_tags = [m['content'] for m in meta_tags if m['content']!=None]
        meta_descr = ' '.join(meta_tags)
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        visible_text = u" ".join(t.strip() for t in visible_texts)
        domain_name = re.sub(r'^(http:\/\/|https:\/\/)?(www\.)?', '', url).split('/')[0]
        text = title + domain_name + meta_descr + visible_text
        url = re.sub(r'^https?:\/\/', '', url)
        return text
    else:
        raise Exception("Error connecting to the website")
    
def retrieve_from_db(cursor,url):
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE url = '{url}'")
    rows = cursor.fetchall()
    if rows:
        return rows[0][2]
    return rows

def set_cache(redis_conn, url, class_number):
    # try:
    redis_conn.set(url, class_number, ex=3600)
    print('aaaa')
    # except:
    #     print('aaaa1')
    #     pass

def set_db(mariadb_conn, cursor, url, class_number, probability):
    # try:
    query = f"INSERT INTO {TABLE_NAME} (url, label, probability) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE label = VALUES(label), probability = VALUES(probability)"
    cursor.execute(query, (url, class_number, probability))
    mariadb_conn.commit()
    print('bbbbbbbb')
    # except:
    #     print('bbbbbbbb1')
    #     pass