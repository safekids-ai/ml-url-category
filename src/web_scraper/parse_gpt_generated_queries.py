import pandas as pd
import requests
from tqdm import tqdm
import requests
import json
from helpers.config import GOOGLE_QUERIES_PATH, BULK_DATA_BUCKET_OR_PATH

#google detects parsers easily, so I found that using serper.dev api was the easiest way to send many queries to google.
#it gives 2500 tokens for free, which is more than sufficient.

def search_google(phrase):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": phrase,
    "num": 100
    })
    headers = {
    'X-API-KEY': 'YOUR SERPER API KEY',
    'Content-Type': 'application/json'
    }
    r = requests.request("POST", url, headers=headers, data=payload)
    return r

with open(GOOGLE_QUERIES_PATH, 'r') as json_file:
    google_queries = json.load(json_file)

for idx,(k,v) in tqdm(enumerate(google_queries.items())):
    cat_dfs = []
    for phrase in v:
        r = search_google(phrase)
        df = pd.DataFrame(eval(r.content)['organic'])[['title','link','snippet']]
        df['category'] = k
        df['query']= phrase
        cat_dfs.append(df)
    cat_unif = pd.concat(cat_dfs)
    cat_unif.to_parquet(f'{BULK_DATA_BUCKET_OR_PATH}/cat_{idx}.parquet')