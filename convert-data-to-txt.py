import json
import os



with open(os.path.join('dataset','train_data.json'), encoding='utf-8') as f:
    dataset = json.load(f)

def generate_prompt(data_point):
    return f"""### Caption: {data_point['caption_string']}
### Tags: {data_point['tag_string']}"""

with open('data.txt', 'w') as f:
    for data_point in dataset:
        prompt = generate_prompt(data_point)
        f.write(prompt + '\n\n\n')
    