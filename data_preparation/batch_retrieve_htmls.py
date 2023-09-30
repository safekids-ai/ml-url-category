import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os


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
            with open(f'output/{url}.txt', "w", encoding="utf-8") as file:
                file.write(text)
        else:
            r = requests.get(protocols[1]+url,timeout=5)
            if r.status_code==200:
                text = process_resp(r)
                # Save the retrieved text to a file
                with open(f'output/{url}.txt', "w", encoding="utf-8") as file:
                    file.write(text)
    except:
        pass

def unite_txts(txts,batchid):
    data = []
    for url in txts:
        with open('output/'+url, encoding="utf-8") as f:
            text = f.read()
        os.remove('output/'+url)
        url=url.strip('.txt')
        data.append({'url':url,'text':text})
    df = pd.DataFrame(data)
    df.to_parquet(f'output_parquets/n_{batchid}.parquet')   

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