from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_from_disk
import pickle
import torch
from helpers.utils import compute_metrics, SaveModelAndConfusionMatCallback
from helpers.config import MODEL_NAME, ENCODER_PATH, TRAIN_DATASET_PATH, TEST_DATASET_PATH
from helpers.training_args import train_batch_size, eval_batch_size, num_epochs, warmup_fraction, weight_decay, save_n_last, evaluation_strategy, save_strategy, output_dir


def main():
    train_dataset = load_from_disk(TRAIN_DATASET_PATH)
    test_dataset = load_from_disk(TEST_DATASET_PATH)

    with open(ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)

    class_names = list(encoder.classes_)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(encoder.classes_))

    if torch.cuda.is_available():
        model = model.to('cuda')
    else:
        print("CUDA is not available. Using CPU instead.")
        model = model.to('cpu')

    
    num_samples = len(train_dataset)
    total_steps = (num_samples // train_batch_size) * num_epochs
    warmup_steps = int(total_steps * warmup_fraction)


    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy=evaluation_strategy,
        num_train_epochs = num_epochs,
        per_device_train_batch_size = train_batch_size,
        per_device_eval_batch_size = eval_batch_size,
        warmup_steps = warmup_steps,
        weight_decay = weight_decay,
        logging_dir=None, #'./logs'
        report_to ='tensorboard',
        save_total_limit= save_n_last,
        save_strategy= save_strategy,
        load_best_model_at_end=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics= lambda p: compute_metrics(p, class_names)
    )
    
    callback = SaveModelAndConfusionMatCallback(trainer, test_dataset, class_names)
    trainer.add_callback(callback)

    trainer.train()

if __name__=='__main__':
    main()