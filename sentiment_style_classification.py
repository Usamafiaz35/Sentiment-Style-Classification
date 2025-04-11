# -*- coding: utf-8 -*-
"""Sentiment-style classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10Zxfx2EnwOfyUel7X2kqnPUyPsM-cudw
"""

from huggingface_hub import notebook_login
notebook_login()

!pip install datasets

from datasets import load_dataset

# Load GLUE MRPC
dataset = load_dataset("glue", "mrpc")
dataset

datasets = dataset["train"]
datasets[0]

dataset['train'].features

from transformers import AutoTokenizer

model_checkpoint = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

def tokenize_function(example):
    return tokenizer(example["sentence1"], example["sentence2"], truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="tf")

tf_train = tokenized_datasets["train"].to_tf_dataset(
    columns=["input_ids", "attention_mask", "token_type_ids"],
    label_cols=["label"],
    shuffle=True,
    batch_size=16,
    collate_fn=data_collator
)

tf_valid = tokenized_datasets["validation"].to_tf_dataset(
    columns=["input_ids", "attention_mask", "token_type_ids"],
    label_cols=["label"],
    shuffle=False,
    batch_size=16,
    collate_fn=data_collator
)

from transformers import TFAutoModelForSequenceClassification

model = TFAutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=2)

import tensorflow as tf

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"]
)

model.fit(tf_train, validation_data=tf_valid, epochs=3)

preds = model.predict(tf_valid)["logits"]

import numpy as np

class_preds = np.argmax(preds, axis=1)
print(preds.shape, class_preds.shape)

!pip install evaluate

import evaluate

metric = evaluate.load("glue", "mrpc")
metric.compute(predictions=class_preds, references=dataset["validation"]["label"])

from huggingface_hub import HfApi


model.push_to_hub("usama-mrpc-bert-classifier")
tokenizer.push_to_hub("usama-mrpc-bert-classifier")

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-classification", model="usama35/usama-mrpc-bert-classifier")

# Test on new sentence pair
result = pipe({
    "text": "He said the food was great.",
    "text_pair": "pakistan is great."
})

print(result)

