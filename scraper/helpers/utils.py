import pandas as pd
import requests
from bs4.element import Comment
from bs4 import BeautifulSoup
import os
import json

from io import BytesIO
from helpers.config import PROTOCOLS, LOCAL_TMP_DIR, LOCAL_TMP_TXT_PATH, headers

def write_parquet(uuid, client_or_none, bucket_or_directory,mode):
    dict_list = []
    with open(LOCAL_TMP_TXT_PATH, encoding="utf-8") as f:
        for line in f.readlines():
            try:
                dict_list.append(json.loads(line.strip()))
            except:
                pass

    # Creating a DataFrame from the list of dictionaries
    df = pd.DataFrame(dict_list)
    os.remove(LOCAL_TMP_TXT_PATH)
    write_df(df, bucket_or_directory, f'{uuid}.parquet', client_or_none, mode)

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
    meta_tags = [{'name': tag.get('name'), 'content': tag.get('content')} for tag in soup.find_all('meta')][:100]
    headings = {f'h{i}': [tag.string for tag in soup.find_all(f'h{i}')][:100] for i in range(1, 7)}
    images = [{'src': tag['src'], 'alt': tag.get('alt', '')} for tag in soup.find_all('img') if tag.get('src')][:100]
    links = [tag['href'] for tag in soup.find_all('a') if tag.get('href')][:100]
    paragraphs = [tag.get_text() for tag in soup.find_all('p')][:100]
    list_items = [tag.get_text() for tag in soup.find_all('li')][:100]
    bold_texts = [tag.get_text() for tag in soup.find_all(['b', 'strong'])][:100]
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
                data = extract_standard_tags(r,url)
                append_to_tmp_txt(LOCAL_TMP_TXT_PATH, data)              
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
    for column in df.columns[2:-1]:#all cols except url,title and visible_text.
        if all(isinstance(x, list) or pd.isnull(x) for x in df[column]):
            df[column] = df[column].apply(lambda x: x if isinstance(x, list) else [])
        else:
            df[column] = df[column].apply(lambda x: x if isinstance(x, list) else [x])

    if mode == 's3':
        try:
            parquet_buffer = BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            parquet_buffer.seek(0)
            client_or_none.upload_fileobj(parquet_buffer, bucket_or_directory, object_key_or_path)
        except:
            pass
    elif mode == 'local':
        try:
            local_path = os.path.join(bucket_or_directory, object_key_or_path)
            df.to_parquet(local_path, index=False)
        except:
            pass
    else:
        raise ValueError("Invalid mode specified. Use 's3' or 'local'.")