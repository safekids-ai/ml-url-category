import pandas as pd
import requests
import re
from bs4.element import Comment
from bs4 import BeautifulSoup
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from helpers.config import PROTOCOLS, LOCAL_TMP_DIR, LOCAL_TMP_DIR_ZIP, LOCAL_TMP_TXT_PATH, headers
import zipfile

def write_zip(zip_filename,txts,client_or_none,bucket_name):
    with zipfile.ZipFile(f'{LOCAL_TMP_DIR_ZIP}/' + zip_filename, 'w') as zipf:
        for file in txts:
            zipf.write(file, os.path.basename(file))
    if client_or_none:
        client_or_none.upload_file(f'{LOCAL_TMP_DIR_ZIP}/' + zip_filename, bucket_name, zip_filename)
        os.remove(f'{LOCAL_TMP_DIR_ZIP}/'+zip_filename)
    
def write_parquet(uuid, client_or_none, bucket_or_directory,mode):
    with open(LOCAL_TMP_TXT_PATH, encoding="utf-8") as f:
        dict_list = [json.loads(line.strip()) for line in f.readlines()]
    # Creating a DataFrame from the list of dictionaries
    df = pd.DataFrame(dict_list)
    os.remove(LOCAL_TMP_TXT_PATH)
    write_df(df, bucket_or_directory, f'{uuid}.parquet', client_or_none, mode)

#retrieval function which will be called by ThreadPoolExecutor
# def retrieve(url):
#     def process_resp(response):
#         soup = BeautifulSoup(response.text,'html.parser')
#         text = soup.text.strip()
#         text = re.sub('[\n\t\r]+', '\n', text)
#         text = re.sub('s+', ' ', text)
#         return text
#     try:
#         # Try both HTTP and HTTPS protocols to retrieve the content
#         for protocol in PROTOCOLS:
#             r = requests.get(protocol+url, timeout=2)
#             if r.status_code == 200:
#                 text = process_resp(r)
#                 # Save the retrieved text to a file
#                 with open(f'{LOCAL_TMP_DIR}/{url}.txt', "w", encoding="utf-8") as file:
#                     file.write(text)
#             break
#     except:
#         pass


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def extract_standard_tags(response,url):
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.string if soup.title else None
    meta_tags = [{'name': tag.get('name'), 'content': tag.get('content')} for tag in soup.find_all('meta')]
    headings = {f'h{i}': [tag.string for tag in soup.find_all(f'h{i}')] for i in range(1, 7)}
    images = [{'src': tag['src'], 'alt': tag.get('alt', '')} for tag in soup.find_all('img') if tag.get('src')]
    links = [tag['href'] for tag in soup.find_all('a') if tag.get('href')]
    paragraphs = [tag.get_text() for tag in soup.find_all('p')]
    list_items = [tag.get_text() for tag in soup.find_all('li')]
    bold_texts = [tag.get_text() for tag in soup.find_all(['b', 'strong'])]
    # italic_texts = [tag.get_text() for tag in soup.find_all(['i', 'em'])]
    # blockquotes = [tag.get_text() for tag in soup.find_all('blockquote')]
    # comments = [str(comment) for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    visible_text = u" ".join(t.strip() for t in visible_texts)
    
    return {'url': url,
        'title': title,
        'meta_tags': meta_tags,
        'headings': headings,
        'images': images,
        'links': links,
        'paragraphs': paragraphs,
        'list_items': list_items,
        'bold_texts': bold_texts,
        # 'italic_texts': italic_texts,
        # 'blockquotes': blockquotes,
        # 'comments': comments,
        'visible_text': visible_text
    }

def append_to_tmp_txt(tmp_txt_path,url_dict):
    with open(tmp_txt_path, 'a',encoding="utf-8") as file:
        json.dump(url_dict, file)
        file.write("\n")

def retrieve(url):
    try:
        # Try both HTTP and HTTPS protocols to retrieve the content
        for protocol in PROTOCOLS:
            r = requests.get(protocol+url,headers=headers, timeout=5)
            if r.status_code == 200:
                data = extract_standard_tags(r)
                append_to_tmp_txt(LOCAL_TMP_TXT_PATH, data)
                # with open(f'{LOCAL_TMP_DIR}/{url}.html', "w", encoding="utf-8") as file:
                #     file.write(r.text)
                
            break
    except:
        pass


def unite_txts(txts, uuid, client_or_none, bucket_or_directory,mode):
    data = []
    for url in txts:
        with open(f'{LOCAL_TMP_DIR}/'+url, encoding="utf-8") as f:
            text = f.read()
        os.remove(f'{LOCAL_TMP_DIR}/'+url)
        url=url.strip('.txt')
        data.append({'url':url,'text':text})
    df = pd.DataFrame(data)
    write_df(df, bucket_or_directory, f'{uuid}.parquet', client_or_none, mode)



def write_df(df, bucket_or_directory, object_key_or_path, client_or_none, mode='s3'):
    if mode == 's3':
        parquet_buffer = BytesIO()
        pq.write_table(pa.Table.from_pandas(df), parquet_buffer)
        # Upload Parquet file to S3
        parquet_buffer.seek(0)
        client_or_none.upload_fileobj(parquet_buffer, bucket_or_directory, object_key_or_path)
    elif mode == 'local':
        # Write to local file system
        local_path = os.path.join(bucket_or_directory, object_key_or_path)
        pq.write_table(pa.Table.from_pandas(df), local_path)
    else:
        raise ValueError("Invalid mode specified. Use 's3' or 'local'.")


#This is needed if parsing was interrupted and you are continueing download from the previous batch. 
def get_max_batch_N(s3, bucket_or_directory, mode, instance_id):
    files = []
    # Create a paginator for listing objects in the S3 bucket
    if mode=='s3':
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_or_directory)

        # Iterate over each page of results
        for page in pages:
            # Check if there are any contents in the page
            if "Contents" in page:
                for obj in page["Contents"]:
                    filename = obj["Key"]
                    if filename.endswith('.zip') & filename.startswith(str(instance_id)):
                        files.append(filename.split('n')[0].split('_')[1])
        files=[file for file in files if file!='']
        files=[int(file) for file in files]
        if files == []:
            return 0
    elif mode=='local':
        # List files in the local directory
        for filename in os.listdir(bucket_or_directory):
            if filename.endswith('.zip'):
                try:
                    batch_number = int(filename.split('n')[0].split('_')[1])
                    files.append(batch_number)
                except ValueError:
                    # If conversion to int fails, skip this file
                    continue

        if not files:
            return 0
    return max(files)+1
