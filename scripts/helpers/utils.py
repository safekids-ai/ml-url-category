import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from transformers import TrainerCallback
import seaborn as sns



def compute_metrics(p, class_names):
    preds = np.argmax(p.predictions, axis=1)
    labels = p.label_ids
    precision = precision_score(labels, preds, average=None)
    recall = recall_score(labels, preds, average=None)
    f1 = f1_score(labels, preds, average=None)

    precision_overall = precision_score(labels, preds, average='weighted')
    recall_overall = recall_score(labels, preds, average='weighted')
    f1_overall = f1_score(labels, preds, average='weighted')

    metrics = {
        'precision_per_class': {class_names[i]: val for i, val in enumerate(precision)},
        'recall_per_class': {class_names[i]: val for i, val in enumerate(recall)},
        'f1_per_class': {class_names[i]: val for i, val in enumerate(f1)},
        'precision_overall': precision_overall,
        'recall_overall': recall_overall,
        'f1_overall': f1_overall
    }
    return metrics


class SaveModelAndConfusionMatCallback(TrainerCallback):
    def __init__(self, trainer, test_dataset, class_names):
        self.test_dataset = test_dataset
        self.trainer = trainer
        self.class_names = class_names

    def on_epoch_end(self, args, state, control, **kwargs):

        predictions, labels, _ = self.trainer.predict(self.test_dataset)
        preds = np.argmax(predictions, axis=1)

        cm = confusion_matrix(labels, preds)

        plt.figure(figsize=(15, 12))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=self.class_names, yticklabels=self.class_names)
        plt.xlabel('Predicted labels')
        plt.ylabel('True labels')
        plt.savefig(f"./results/confusion_matrix_epoch_{int(state.epoch)}.png")
        plt.close()
