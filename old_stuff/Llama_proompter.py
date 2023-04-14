import requests
import os
import json
from itertools import chain
import random
from llama_cpp import Llama


TAG_JSON_DIR = r'dataset\tag_data.json'
MODEL = r"C:\Programs\llamacpp\models\vicuna-13b\ggml-vicuna-13b-4bit-rev1.bin"

PROMPT_FORMATS = [
    "Write a caption with a highly neutral and objective tone using all the details from these Danbooru tags as keywords in under 200 words.\n {inputs}",
    "Write a concise and objective description for an illustration using the given keywords in under 200 words: {inputs}",
    "Describe a scene very objectively using these Danbooru tags as keywords in under 200 words.\n {inputs}",
]
LONG_PROMPT_FORMATS = [
    "Write a complete and objective description for an anime illustration using all the given keywords: {inputs}"
]

TAG_TRANSLATION_LOOKUP = {
    "+ +": "plus symbol eyes",
    "+++": "chattering",
    ". .": "dot eyes",
    "0 0": "surprised face",
    ":3": "cat face",
    ":<": "sturgeon face",
    ":>": "smile",
    ":d": "smile",
    ":i": "pouting",
    ":T": "pouting",
    ":o": "open mouth surprised face",
    ":|": "poker face",
    ":/": "ambivalent face",
    ";)": "winking closed mouth smile",
    ";d": "winking smile",
    ";p": "winking tongue out",
    "= =": "sleepy bored face",
    "> <": "eyes shut gleeful face",
    "@ @": "dizzy swirl eyes",
    "^ ^": "closed eye smile",
    "^^^": "surprise",
    "^o^": "open mouth closed eye smile",
    "ahoge": "ahoge cowlick",
    "double v": "double peace sign hands",
    "doyagao": "smug",
    "o o": "surprised face",
    "serafuku": "sailor school uniform",
    "t t": "stream of tears",
    "v": "peace sign hands",
    "xd": "eyes shut laughing",
    "zettai ryouiki": "skin between skirt and knee socks",
    "| |": "emotionless eyes",
}

with open(TAG_JSON_DIR, 'r') as f:
    data = json.load(f)

llm = Llama(model_path=MODEL, n_ctx=1024)

def replace_tags(data_point):
    general_tags = data_point["general"]
    general_tags_translated = [TAG_TRANSLATION_LOOKUP.get(x, x) for x in general_tags]
    data_point["general"] = sorted(general_tags_translated)
    return data_point


# print(replace_tags({'general':[';d','^^^','bruh']}))


def flatten_to_string_input(data_point):
    keys = ("copyright", "character", "artist", "general", "metadata")
    return ", ".join(list(chain.from_iterable([data_point[x] for x in keys])))


# print(flatten_to_string_input(data[0]))

def get_prompt(inputs, prompt_format='random'):
    if len(inputs) > 1200:
        prompt = LONG_PROMPT_FORMATS[0].format(inputs=inputs)
    else:
        if type(prompt_format) != str:
            prompt = PROMPT_FORMATS[prompt_format].format(inputs=inputs)
        else:
            prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    return prompt

def get_caption(data_point, prompt_format='random'):
    data_point_translated = replace_tags(data_point)
    inputs = flatten_to_string_input(data_point_translated)
    prompt = get_prompt(inputs, prompt_format)
    print(prompt)
    print()
    messages = [{"role": "user", "content": prompt}]
    response = llm(f"### Human: {random.choice(PROMPT_FORMATS).format(tags=tags)} ### Assistant:", max_tokens=300, stop=["### Human:"], echo=True)
    print(response)
    caption = response["choices"][0]["text"]
    print(caption.split())

    # response = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=messages,
    #     temperature=TEMPERATURE,
    # )
    # caption = response["choices"][0]["message"]["content"]
    # return caption

response = llm(f"### Human: {random.choice(PROMPT_FORMATS).format(tags=tags)} ### Assistant:", max_tokens=300, stop=["### Human:"], echo=True)
print(response)
caption = response["choices"][0]["text"]
print(caption)


