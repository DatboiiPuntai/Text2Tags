from utils import similar_tag
import json
import requests

# Server address
server = "127.0.0.1"

# Generation parameters
# Reference: https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig
params = {
    'max_new_tokens': 300,
    'do_sample': True,
    'temperature': 0.7,
    'top_p': 0.5,
    'typical_p': 1,
    'repetition_penalty': 1.1,
    'encoder_repetition_penalty': 1,
    'top_k': 40,
    'min_length': 0,
    'no_repeat_ngram_size': 0,
    'num_beams': 1,
    'penalty_alpha': 0,
    'length_penalty': 1,
    'early_stopping': False,
    'seed': -1,
    'add_bos_token': True,
    'truncation_length': 2048,
    'ban_eos_token': False,
    'skip_special_tokens': True,
    'stopping_strings': [],
}

# Input prompt
data = json.load(open(r"dataset/test_data_v2.json"))
tag_dict = similar_tag.load_dict()

for data_point in data[:5]:
    caption = data_point['caption_string']
    tags = data_point['tag_string'].split(', ')

    prompt = f"### Caption: {caption}\n### Tags: "

    payload = json.dumps([prompt, params])

    response = requests.post(f"http://{server}:7860/run/textgen", json={
        "data": [
            payload
        ]
    }).json()

    preds = response['data'][0].split('### Tags: ')[1]
    corrected_preds = similar_tag.correct_tags(preds.split(', '), tag_dict)

    print(f"Correct tags: {', '.join(tags)}")
    print()
    print(f"Predicted tags: {', '.join(corrected_preds)}")
    print()
    print(f"Raw preds: {preds}")
    print()
    print()