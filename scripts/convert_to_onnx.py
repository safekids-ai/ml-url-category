import pickle
from transformers import AutoModelForSequenceClassification
from pathlib import Path
import torch
from transformers.convert_graph_to_onnx import convert
from helpers.config import ENCODER_PATH, LAST_CHECKPOINT_PATH, ONNX_MODEL_PATH, MODEL_NAME

def main():
    with open(ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)

    model_checkpoint = Path(LAST_CHECKPOINT_PATH)
    onnx_model_path = Path(ONNX_MODEL_PATH)

    labels_len = len(encoder.classes_)

    model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=labels_len)

    device = torch.device("cpu")
    model.to(device)

    convert(
        framework="pt",
        model=model, 
        output=ONNX_MODEL_PATH,
        opset=11,
        tokenizer= MODEL_NAME
    )

    if onnx_model_path.exists():
        print('Model converted to onnx', ONNX_MODEL_PATH)

if __name__=='__main__':
    main()