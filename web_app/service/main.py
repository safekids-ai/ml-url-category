from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pydantic import BaseModel
import pickle
import onnxruntime
import numpy as np
from transformers import AutoTokenizer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlparse
import redis
import os
import json
import re

from service_utils import init_redis, load_tokenizer_and_encoder, load_model, check_cache, retrieve_from_web, retrieve_from_db, init_mariadb, remove_www, set_cache, set_db
# from service_config import HEADERS, REDIS_PASSWORD
# from service_config import TOKENIZER_CHECKPOINT, ONNX_MODEL_PATH, ENCODER_PATH



app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/sdk"), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


redis_conn = init_redis()

mariadb_conn = init_mariadb()
cursor = mariadb_conn.cursor()

tokenizer, encoder = load_tokenizer_and_encoder()
session = load_model()

class Item(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return Path("/app/sdk/index.html").read_text()


@app.post("/predict/")
def predict(item: Item):
    cache_res = db_res = class_number = None
    url_str = remove_www(item.text)
    if len(url_str.split('.')) < 2:
        return {"prediction": f'Enter valid URL'}
    try:
        cache_res = check_cache(redis_conn,url_str)
    except:
        redis_conn = init_redis()
        cache_res = check_cache(redis_conn,url_str)
    if cache_res:
        class_number = int(cache_res)
        pred_type = 'cache'
    else:
        try:
            db_res = retrieve_from_db(cursor, url_str)
        except:
            mariadb_conn = init_mariadb()
            cursor = mariadb_conn.cursor()
            db_res = retrieve_from_db(cursor, url_str)
        if db_res:
            class_number = db_res
            class_number = int(class_number)
            pred_type = 'db'
            set_cache(redis_conn, url_str, class_number)
        else:
            try:
                class_number = retrieve_from_web(url_str,tokenizer,session,encoder)
                pred_type = 'web'
                url_str = re.sub(r'^https?:\/\/', '', url_str)
                set_cache(redis_conn, url_str, class_number)
                set_db(mariadb_conn, cursor, url_str, class_number)
            except:
                return {"prediction": f'Error Occured, Try Again..'}
    # return class_number
    
    category = encoder.classes_[class_number]
    return {"prediction": f'Predicted class of {url_str} from {pred_type} is: <b style="color:Tomato;">{category}</b>'}