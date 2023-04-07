import json
import os

DATASET_FILENAME = 'test_data.json'
DATASET_PATH = 'test_dataset'
INSTRUCTION = 'Write a highly descriptive and objective caption for an anime illustration using the given danbooru tags.'

with open(os.path.join(DATASET_PATH,DATASET_FILENAME), encoding='utf-8') as f:
    dataset = json.load(f)
print(f'Loaded {len(dataset)} records from {DATASET_PATH}')


alpaca_dataset = [{
    "instruction": INSTRUCTION,
    "input": x['tags'],
    "output": x['caption']} 
    for x in dataset]

print(alpaca_dataset[0])

json_object = json.dumps(alpaca_dataset, indent=4)

with open(os.path.join(DATASET_PATH, f'{DATASET_FILENAME.split(".")[0]}_alpaca.json'), 'w') as outfile:
    outfile.write(json_object)