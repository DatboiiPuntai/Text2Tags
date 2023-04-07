import json
import os

DATASET_FILENAME = 'train_data.json'
DATASET_PATH = 'small_dataset'

with open(os.path.join(DATASET_PATH,DATASET_FILENAME), encoding='utf-8') as f:
    dataset = json.load(f)
print(f'Loaded {len(dataset)} records from {DATASET_PATH}')


for x in dataset:
    for k, v in x.items():
        print(f'{k}: {v}')
        print()
    print()