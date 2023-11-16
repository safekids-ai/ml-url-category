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

headers = {
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

# Load your model and tokenizer here
tokenizer_checkpoint = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_checkpoint)

ONNX_MODEL_PATH = '/app/model/model.onnx'
ENCODER_PATH = '/app/model/encoder.pkl'

with open(ENCODER_PATH, 'rb') as f:
    encoder = pickle.load(f)


providers = onnxruntime.get_available_providers()
if 'CUDAExecutionProvider' in providers:
    session = onnxruntime.InferenceSession(ONNX_MODEL_PATH, providers=['CUDAExecutionProvider'])
else:
    session = onnxruntime.InferenceSession(ONNX_MODEL_PATH, providers=['CPUExecutionProvider'])
# session = onnxruntime.InferenceSession(ONNX_MODEL_PATH, providers=['CUDAExecutionProvider','CPUExecutionProvider'])

class Item(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return Path("/app/sdk/index.html").read_text()

def retrieve_text(url):
    if not urlparse(url).scheme:
        url = "http://" + url
    if len(url.split('.'))<2:
        raise Exception("Enter valid url")
    response = requests.get(url)
    if response.status_code == 200:
        resp = response.content
        sp = BeautifulSoup(resp,'html.parser')
        text = sp.text
        return text
    else:
        raise Exception("Error connecting to the website")


@app.post("/predict/")
def predict(item: Item):
    url = item.text
    text = retrieve_text(url)
    inputs = tokenizer(text, return_tensors="np", max_length=512, truncation=True, padding=True)
    onnx_inputs = {k: v for k, v in inputs.items() if k in [i.name for i in session.get_inputs()]}
    outputs = session.run(None, onnx_inputs)[0]
    probabilities = np.exp(outputs) / np.sum(np.exp(outputs), axis=1, keepdims=True)
    pred_class = encoder.classes_[np.argmax(probabilities, axis=1)]
    return {"prediction": pred_class.tolist()}