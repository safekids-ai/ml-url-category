from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from service_utils import init_redis, load_tokenizer_and_encoder, load_model, check_cache, retrieve_from_web, retrieve_from_db, init_mariadb, remove_www_http_https, set_cache, set_db



app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/assets"), name="static")

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
    return Path("/app/assets/index.html").read_text()

class WebsiteData(BaseModel):
    url: str
    category: str

@app.post("/add_to_db/")
def add_to_db(data: WebsiteData):
    url_str = data.url
    category = data.category
    url_str = remove_www_http_https(url_str).lower()
    class_number = int(encoder.transform([category])[0])
    set_cache(redis_conn, url_str.lower(), class_number)
    set_db(mariadb_conn = mariadb_conn, cursor = cursor, url = url_str.lower(), class_number = class_number, probability = 1)
    return {"message": "Data added to database successfully"}


@app.post("/predict/")
def predict(item: Item):
    cache_res = db_res = class_number = None
    url_str = remove_www_http_https(item.text)
    if len(url_str.split('.')) < 2:
        return {"prediction": f'Enter valid URL'}
    try:
        cache_res = check_cache(redis_conn,url_str.lower())
    except:
        redis_conn = init_redis()
        cache_res = check_cache(redis_conn,url_str.lower())
    if cache_res:
        class_number = int(cache_res)
        pred_type = 'cache'
    else:
        try:
            db_res = retrieve_from_db(cursor, url_str.lower())
        except:
            mariadb_conn = init_mariadb()
            cursor = mariadb_conn.cursor()
            db_res = retrieve_from_db(cursor, url_str.lower())
        if isinstance(db_res, int):
            class_number = db_res
            class_number = int(class_number)
            pred_type = 'db'
            set_cache(redis_conn, url_str.lower(), class_number)
        else:
            try:
                class_number,probability = retrieve_from_web(url_str,tokenizer,session,encoder)
                pred_type = 'web'
                print(url_str)
                set_cache(redis_conn, url_str.lower(), class_number)
                set_db(mariadb_conn = mariadb_conn, cursor = cursor, url = url_str.lower(), class_number = class_number, probability= probability)
            except:
                return {"prediction": f'Error Occured, Try Again..'}
    
    category = encoder.classes_[class_number]
    return {"prediction": f'Predicted class of {url_str} from {pred_type} is: <b style="color:Tomato;">{category}</b>'}