import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import boto3
import pyarrow as pa
from io import BytesIO


s3_client = boto3.client('s3')
os.makedirs("txt_output", exist_ok=True)

url_df = pd.read_csv('unified_urls.csv')
urls = list(url_df.domain)
batch_size = 1000
max_workers = 30

grouped_urls = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]

protocols = ['https://','http://']


# Function to retrieve and process content from a URL
def retrieve(url):
    def process_resp(response):
        soup = BeautifulSoup(response.text,'html.parser')
        text = soup.text.strip()
        text = re.sub('[\n\t\r]+', '\n', text)
        text = re.sub('s+', ' ', text)
        return text
    try:
        # Try both HTTP and HTTPS protocols to retrieve the content
        r = requests.get(protocols[0]+url,timeout=5)
        if r.status_code==200:
            text = process_resp(r)
            # Save the retrieved text to a file
            with open(f'txt_output/{url}.txt', "w", encoding="utf-8") as file:
                file.write(text)
        else:
            r = requests.get(protocols[1]+url,timeout=5)
            if r.status_code==200:
                text = process_resp(r)
                # Save the retrieved text to a file
                with open(f'txt_output/{url}.txt', "w", encoding="utf-8") as file:
                    file.write(text)
    except:
        pass

def write_df_to_s3(df,s3_bucket,s3_object_key):
    parquet_buffer = BytesIO()
    pa.parquet.write_table(pa.Table.from_pandas(df), parquet_buffer)
    # Upload Parquet file to S3
    parquet_buffer.seek(0)
    s3_client.upload_fileobj(parquet_buffer, s3_bucket, s3_object_key)

def unite_txts(txts,batchid):
    data = []
    for url in txts:
        with open('output/'+url, encoding="utf-8") as f:
            text = f.read()
        os.remove('output/'+url)
        url=url.strip('.txt')
        data.append({'url':url,'text':text})
    df = pd.DataFrame(data)
    write_df_to_s3(df,'batch-htmls',f'n_{batchid}.parquet')
    # df.to_parquet(f'output_parquets/n_{batchid}.parquet')



# Main function to orchestrate the retrieval and processing of URLs
def main():
    for batchid,batch in enumerate(grouped_urls):
        #as filesystems suffer when many small files are saved I process urls in batches of 1000
        #after a single batch I unite htmls in a parquet and move to the next batch.
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Use ThreadPoolExecutor to fetch and save HTML in parallel
            executor.map(retrieve, batch)

        txts = [f for f in os.listdir('output') if f.endswith('txt')]  
        unite_txts(txts,batchid)

if __name__=='__main__':
    main()