import onnxruntime
from transformers import AutoTokenizer
import torch
import pickle
import pandas as pd

YOUR_CSV_PATH = 'input.csv'
OUTPUT_PATH = 'results.csv'
TOKENIZER_PATH = 'web_app/model_binary/tokenizer'
MODEL_ONNX_PATH = 'web_app/model_binary/model.onnx'
ENCODER_PATH = 'web_app/model_binary/encoder.pkl'

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
with open(ENCODER_PATH, 'rb') as f:
    encoder = pickle.load(f)
df = pd.read_csv(YOUR_CSV_PATH)
urls = df['url'].tolist()
texts = list(df['text'])

def main():
    batch_size = 32
    predictions = []
    prediction_probs = []

    session = onnxruntime.InferenceSession(MODEL_ONNX_PATH)
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="np", max_length=512, truncation=True, padding=True)
        inputs['attention_mask'] = inputs['attention_mask'].astype('int64')
        inputs['input_ids'] = inputs['input_ids'].astype('int64')
        onnx_inputs = {k: v for k, v in inputs.items() if k in [i.name for i in session.get_inputs()]}
        outputs = session.run(None, onnx_inputs)
        probabilities = torch.nn.functional.softmax(torch.from_numpy(outputs[0]), dim=1)
        max_probs, predicted_indices = torch.max(probabilities, axis=1)
        predictions.extend(predicted_indices.numpy())
        prediction_probs.extend(max_probs.detach().numpy())
        predicted_class_names = encoder.classes_[predictions]
        results_df = pd.DataFrame({'url': urls, 'category': predicted_class_names, 'probability': prediction_probs})
    results_df.to_csv(OUTPUT_PATH, index=False)


if __name__=='__main__':
    main()