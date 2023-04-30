import json
import os



with open(os.path.join('dataset','test_data.json'), encoding='utf-8') as f:
    dataset = json.load(f)

def generate_prompt(data_point):
    return f"""### Caption: {data_point['caption_string']}
### Tags: {data_point['tag_string']}"""

new_data = [{'caption_string':x['caption_string'],'tag_string':''} for x in dataset]

with open(r'dataset/human_eval.json', 'w') as f:
    f.write(json.dumps(new_data,indent=4))
    