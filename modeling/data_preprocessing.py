from transformers import AutoTokenizer
from datasets import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelEncoder
import nltk
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle
from helpers.config import ENCODER_PATH,TRAIN_DATASET_PATH,TEST_DATASET_PATH,MODEL_NAME,TRAIN_DATA_PATH

nltk.download('stopwords')
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def tokenize_batch(batch):
    return {
        'input_ids': tokenizer(batch['text'], padding='max_length', truncation=True, max_length=512)['input_ids'],
        'attention_mask': tokenizer(batch['text'], padding='max_length', truncation=True, max_length=512)['attention_mask'],
        'labels': batch['encoded_labels']
    }



df = pd.read_parquet(TRAIN_DATA_PATH)

encoder = LabelEncoder()

df['encoded_labels'] = encoder.fit_transform(df['category'])

df['encoded_labels']=df['encoded_labels'].astype(int)

with open(ENCODER_PATH,'wb') as f:
    pickle.dump(encoder,f)



stop_words = set(stopwords.words())
df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['encoded_labels'])

train_dataset = Dataset.from_pandas(train_df,preserve_index=False)
test_dataset = Dataset.from_pandas(test_df,preserve_index=False)


train_dataset = train_dataset.map(tokenize_batch, batched=True,batch_size=32)
test_dataset = test_dataset.map(tokenize_batch, batched=True,batch_size=32)


train_dataset.save_to_disk(TRAIN_DATASET_PATH)
test_dataset.save_to_disk(TEST_DATASET_PATH)