import os
import json
import random
from itertools import chain
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from typing import Union
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAG_JSON_DIR = r"dataset\tag_data_danbooru_test.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7
MAX_THREADS = 10

PROMPT_FORMATS = [
    "Write a caption with a highly neutral and objective tone using all the details from these keywords in under 200 words.\n {inputs}",
    "Write a concise and objective description for an illustration using the given keywords in under 200 words\n {inputs}",
    "Describe a scene very objectively using these keywords in under 200 words.\n {inputs}",
]
LONG_PROMPT_FORMATS = [
    "Write a complete and objective description for an anime illustration using all the given keywords: {inputs}"
]

with open("tag_lookup.txt", "r") as f:
    TAG_LOOKUP = dict(line.strip().split("|||") for line in f)


def main():
    with open(TAG_JSON_DIR, "r") as f:
        data = json.load(f)

    # openai.api_key = OPENAI_API_KEY
    # captioned_data = make_data_multithread(data[:5])
    # with open("captioned_data.json", "w") as outfile:
    #     json.dump(captioned_data, outfile, indent=4)


def replace_tags(tags: list[str]) -> list[str]:
    tags_translated = [TAG_LOOKUP.get(x, x) for x in tags]
    return tags_translated


# print(replace_tags([';d','^^^','bruh']))


def generate_inputs(data_point: dict[str, list[str]]) -> str:
    data_point["general"] = replace_tags(data_point["general"])
    inputs = ""
    for k in ("copyright", "character", "artist", "general", "metadata"):
        tags = data_point[k]
        if tags: inputs += f"{k}: {', '.join(tags)}\n"

    return inputs


def generate_prompt(inputs: str, prompt_format: Union[str, int] = "random") -> str:
    if len(inputs) > 1200:
        prompt = LONG_PROMPT_FORMATS[0].format(inputs=inputs)
    else:
        if type(prompt_format) != str:
            prompt = PROMPT_FORMATS[prompt_format].format(inputs=inputs)
        else:
            prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    return prompt


def generate_caption(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    # Use the OpenAI API to generate a response using the messages and other parameters
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
    )
    # Get the caption string from the response and return it
    caption = response["choices"][0]["message"]["content"]
    return caption


def make_data(data_point: dict, prompt_format: str = "random") -> dict:
    # Flatten the modified data_point dictionary to a string input using a helper function
    inputs = generate_inputs(data_point)

    # Generate a prompt string using a helper function
    prompt = generate_prompt(inputs, prompt_format)

    # Generate a caption string using a helper function
    caption = generate_caption(prompt)

    # Add the inputs, prompt, and caption strings to the data_point dictionary
    data_point["inputs"] = inputs
    data_point["prompt"] = prompt
    data_point["caption"] = caption

    # Return the modified data_point dictionary
    return data_point


def make_data_multithread(data):
    threads = min(MAX_THREADS, len(data))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        captioned_data = executor.map(make_data, data)
    return list(captioned_data)


# if __name__ == "__main__":
#     main()
