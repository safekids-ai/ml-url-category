import pandas as pd
import uuid
from concurrent.futures import ThreadPoolExecutor
import os
import boto3
from io import StringIO
from helpers.utils import retrieve, unite_txts, get_max_batch_N
from helpers.config import MAX_WORKERS, BULK_DATA_PATH, BULK_DATA_BUCKET, FILE_KEY, BUCKET_TO_SAVE, LOCAL_TMP_DIR
from tqdm import tqdm

import argparse
# Add an argument parser to handle the input argument for reading source
parser = argparse.ArgumentParser(description='Process read source.')
parser.add_argument('--mode', type=str, choices=['s3', 'local'],
                    help='Specify where to read files from and write to: "s3" for Amazon S3, "local" for local filesystem.')

# Parse arguments
args = parser.parse_args()
mode = args.mode


# Use the argument to decide where to read the files from
if mode == 's3':
    s3_client = boto3.client('s3')
    #I stored all my urls on s3, but since we want to load it from local, you should run it run it with local mode.
    response = s3_client.get_object(Bucket= BULK_DATA_BUCKET, Key=FILE_KEY)
    content = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(content))
elif mode == 'local':
    df = pd.read_json(BULK_DATA_PATH)

#This script was running on 3 different instances for more than a week. It won't be needed if you want to pull less than 5m urls probably,
# or if time is not your priority.


os.makedirs(LOCAL_TMP_DIR, exist_ok=True)







#I group urls in 1000s.
df['batchid']=df.index//1000

#I used this block just several times, when kernel died for unknown reasons and I wanted to continue from where I left off.
batch_to_start_from = get_max_batch_N(s3_client, BUCKET_TO_SAVE, mode)
if batch_to_start_from>0:
    batch_to_start_from=batch_to_start_from+1
df = df[df['batchid']>=batch_to_start_from]

#this is the list on which we will iterate. It is list of urls grouped in 1000s.
#ThreadPoolExecutor will iterate on these batches and try to process in MAX_WORKERS number of parallel urls.
#After Downloading 1000 htmls, unite them in parquet and write to s3.
#I did that because I was restricted in space locally.
grouped_urls = df.groupby('batchid')['domain'].apply(list).tolist()

def main():
    for batchid, batch in tqdm(enumerate(grouped_urls)):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Use ThreadPoolExecutor to fetch and save HTML in parallel
            executor.map(retrieve, batch)

        txts = [f for f in os.listdir('txt_output') if f.endswith('txt')]
        unite_txts(txts, f'{batchid+batch_to_start_from}_n_{uuid.uuid4()}', s3_client, BUCKET_TO_SAVE)

if __name__ == "__main__":
    main()