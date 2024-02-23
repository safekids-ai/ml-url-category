import pandas as pd
import uuid
from concurrent.futures import ThreadPoolExecutor
import os
import boto3
from helpers.utils import retrieve, get_max_batch_N, write_parquet
from helpers.config import MAX_WORKERS, BULK_DATA_BUCKET_OR_PATH, FILE_KEY, BUCKET_OR_PATH_TO_SAVE, LOCAL_TMP_DIR, LOCAL_TMP_TXT_PATH
from tqdm import tqdm
import argparse
import os

from dotenv import load_dotenv
load_dotenv() 
Access_key = os.getenv('Access_key')
Secret_access_key = os.getenv('Secret_access_key')


instance_id = 2
FILE_KEY = FILE_KEY.format(instance_id)

parser = argparse.ArgumentParser(description='Process read source.')
parser.add_argument('--mode', type=str, choices=['s3', 'local'],
                    help='Specify where to read files from and write to: "s3" for Amazon S3, "local" for local filesystem.')

args = parser.parse_args()
mode = 's3'

def batch_strings(input_list, N):
    return [input_list[i:i + N] for i in range(0, len(input_list), N)]

# Use the argument to decide where to read the files from
if mode == 's3':
    s3_client = boto3.client('s3',
                  aws_access_key_id=Access_key,
                  aws_secret_access_key=Secret_access_key)
    #I stored all my urls on s3, but since we want to load it from local, you should run it run it with local mode.
    response = s3_client.get_object(Bucket= BULK_DATA_BUCKET_OR_PATH, Key=FILE_KEY)
    content = response['Body'].read().decode('utf-8')
    url_list = content.splitlines()
elif mode == 'local':
    with open(BULK_DATA_BUCKET_OR_PATH,'r') as f:
        url_list = f.readlines()
    
    s3_client = None
else:
    raise Exception("choose 'local' or 's3' mode. eg: --mode local")

#This script was running on 3 different instances for more than a week. It won't be needed if you want to pull less than 5m urls probably,
# or if time is not your priority.


os.makedirs(LOCAL_TMP_DIR, exist_ok=True)


#I used this block just several times, when kernel died for unknown reasons and I wanted to continue from where I left off.
batch_to_start_from = get_max_batch_N(s3_client, BUCKET_OR_PATH_TO_SAVE, mode, instance_id)
batch_to_start_from=batch_to_start_from-2243


#this is the list on which we will iterate. It is list of urls grouped in 1000s.
#ThreadPoolExecutor will iterate on these batches and try to process in MAX_WORKERS number of parallel urls.
#After Downloading 1000 htmls, unite them in parquet and write to s3.
#I did that because I was restricted in space locally.

url_list = [url.strip() for url in url_list]
N = 1000 # replace with your desired batch size
grouped_urls = batch_strings(url_list, N)

f'{batch_to_start_from}/{len(grouped_urls)}'

grouped_urls = grouped_urls[batch_to_start_from+1:]

print(len(grouped_urls))

for batchid, batch in tqdm(enumerate(grouped_urls)):
    unique_id = f'{instance_id}_{batchid+batch_to_start_from+2244}_n_{uuid.uuid4()}'
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Use ThreadPoolExecutor to fetch and save HTML in parallel
        executor.map(retrieve, batch)
    if os.path.exists(LOCAL_TMP_TXT_PATH):
        write_parquet(unique_id, s3_client, BUCKET_OR_PATH_TO_SAVE,mode)