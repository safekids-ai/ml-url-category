import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import os
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from helpers.config import PROTOCOLS, LOCAL_TMP_DIR


#retrieval function which will be called by ThreadPoolExecutor
def retrieve(url):
    def process_resp(response):
        soup = BeautifulSoup(response.text,'html.parser')
        text = soup.text.strip()
        text = re.sub('[\n\t\r]+', '\n', text)
        text = re.sub('s+', ' ', text)
        return text
    try:
        # Try both HTTP and HTTPS protocols to retrieve the content
        for protocol in PROTOCOLS:
            r = requests.get(protocol+url, timeout=2)
            if r.status_code == 200:
                text = process_resp(r)
                # Save the retrieved text to a file
                with open(f'{LOCAL_TMP_DIR}/{url}.txt', "w", encoding="utf-8") as file:
                    file.write(text)
            break
    except:
        pass


def unite_txts(txts, uuid, s3_client, bucket_name):
    data = []
    for url in txts:
        with open('{LOCAL_TMP_DIR}/'+url, encoding="utf-8") as f:
            text = f.read()
        os.remove('{LOCAL_TMP_DIR}/'+url)
        url=url.strip('.txt')
        data.append({'url':url,'text':text})
    df = pd.DataFrame(data)
    write_df_to_s3(df, bucket_name,f'{uuid}.parquet', s3_client)


def write_df_to_s3(df,s3_bucket, s3_object_key, s3_client):
    parquet_buffer = BytesIO()
    pq.write_table(pa.Table.from_pandas(df), parquet_buffer)
    # Upload Parquet file to S3
    parquet_buffer.seek(0)
    s3_client.upload_fileobj(parquet_buffer, s3_bucket, s3_object_key)


#This is needed if parsing was interrupted and you are continueing download from the previous batch. 
def get_max_batch_N(s3, path, mode):
    files = []
    # Create a paginator for listing objects in the S3 bucket
    if mode=='s3':
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=path)

        # Iterate over each page of results
        for page in pages:
            # Check if there are any contents in the page
            if "Contents" in page:
                for obj in page["Contents"]:
                    filename = obj["Key"]
                    # Check if the filename starts with '1_n'
                    if filename.endswith('.parquet'):
                        files.append(filename.split('n')[0].split('_')[1])
        files=[file for file in files if file!='']
        files=[int(file) for file in files]
        if files == []:
            return 0
    elif mode=='local':
        # List files in the local directory
        for filename in os.listdir(path):
            if filename.endswith('.parquet'):
                try:
                    batch_number = int(filename.split('n')[0].split('_')[1])
                    files.append(batch_number)
                except ValueError:
                    # If conversion to int fails, skip this file
                    continue

        if not files:
            return 0
    return max(files)+1
