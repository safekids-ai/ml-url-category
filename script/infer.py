import onnxruntime
import numpy as np
from transformers import AutoTokenizer
import torch
import pickle
from helpers.config import ENCODER_PATH

tokenizer_checkpoint = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_checkpoint)

def main():
    with open(ENCODER_PATH, 'rb') as f:
            encoder = pickle.load(f)

    text = "Your example text goes here"
    inputs = tokenizer(text, return_tensors="np", max_length=512, truncation=True, padding="max_length")
    onnx_model_path = Path("/content/drive/MyDrive/model_data/data/quantized/model.onnx")
    session = onnxruntime.InferenceSession(onnx_model_path)
    onnx_inputs = {k: v for k, v in inputs.items() if k in [i.name for i in session.get_inputs()]}
    outputs = session.run(None, onnx_inputs)

    probabilities = torch.nn.functional.softmax(torch.from_numpy(outputs[0]), dim=-1)

    print(probabilities.numpy())


    class_names = encoder.classes_

    predicted_index = np.argmax(probabilities, axis=1)

    predicted_class_name = class_names[predicted_index]
    print(predicted_class_name)


if __name__=='__main__':
    main()