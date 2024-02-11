import onnxruntime
import numpy as np
from transformers import AutoTokenizer
import torch
import pickle
from helpers.config import ENCODER_PATH, PATH_TO_BULK_DATA, ONNX_MODEL_PATH
import pandas as pd

tokenizer_checkpoint = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_checkpoint)

def main():
    with open(ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)

    df = pd.read_parquet(PATH_TO_BULK_DATA)
    urls = df['url'].tolist()
    texts = list(df['text'])
    del df

    batch_size = 32  # or whatever size your GPU can comfortably handle
    predictions = []

    session = onnxruntime.InferenceSession(ONNX_MODEL_PATH)
    for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = tokenizer(batch_texts, return_tensors="np", max_length=512, 
                            truncation=True, padding=True)
            onnx_inputs = {k: v for k, v in inputs.items() if k in [i.name for i in session.get_inputs()]}
            outputs = session.run(None, onnx_inputs)
            probabilities = torch.nn.functional.softmax(torch.from_numpy(outputs[0]), dim=1)
            predicted_indices = np.argmax(probabilities, axis=1)
            predictions.extend(predicted_indices)

    predicted_class_names = encoder.classes_[predictions]
    results_df = pd.DataFrame({'url': urls, 'category': predicted_class_names})
    results_df.to_json('predicted_labels.json', orient='records', lines=True)

if __name__=='__main__':
    main()