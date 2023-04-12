import json
import os

DATASET_FILENAME = 'test_data_alpaca.json'
DATASET_PATH = 'test_dataset'

with open(os.path.join(DATASET_PATH,DATASET_FILENAME), encoding='utf-8') as f:
    dataset = json.load(f)
print(f'Loaded {len(dataset)} records from {DATASET_PATH}')

def generate_prompt(data_point):
    return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
{data_point["instruction"]}
### Input:
{data_point["input"]}
### Response:
{data_point["output"]}"""

print(generate_prompt(dataset[1]))

# with open('data.txt', 'w') as f:
#     for data_point in dataset:
#         prompt = generate_prompt(data_point)
#         f.write(prompt + '\n\n\n')
    