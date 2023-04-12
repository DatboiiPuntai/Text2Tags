import requests
import os
import json
from itertools import chain
import random
from llama_cpp import Llama


TAG_JSON_DIR = r'dataset\tag_data.json'
MODEL = r"C:\Programs\llamacpp\models\vicuna-13b\ggml-vicuna-13b-4bit-rev1.bin"
TEMPERATURE = 0.8

PROMPT_FORMATS = [
    "Write a caption with a highly neutral and objective tone using ALL the details from these Danbooru tags as keywords including the artist in under 200 words {tags}",
    "Describe an anime illustration with a highly neutral and objective tone using ALL the details from these Danbooru tags as keywords including the artist in about 200 words {tags}",
    ]

with open(TAG_JSON_DIR, 'r') as f:
    data = json.load(f)

def convert_to_string(tag_dict):
    return ', '.join(list(chain.from_iterable(tag_dict.values())))
tags = convert_to_string(data[4])


llm = Llama(model_path=MODEL, n_ctx=1024)
response = llm(f"### Human: {random.choice(PROMPT_FORMATS).format(tags=tags)} ### Assistant:", max_tokens=300, stop=["### Human:"], echo=True)
print(response)
caption = response["choices"][0]["text"]
print(caption)


