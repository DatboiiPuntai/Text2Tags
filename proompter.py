import os
import json
import random
from itertools import chain
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from typing import Union
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAG_JSON_DIR = r"dataset\test.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.6
MAX_THREADS = 10

PROMPT_FORMATS = [
    "Reply with a complete description of an artworkusing these keywords. Do not infer anything.\n{inputs}",
    "Using these keywords, reply with a creative and eloquent caption.\n{inputs}",
    "Reply with a short and summarized description of an artwork based on these keywords. Do not go over 75 words.\n{inputs}",
    "Reply with only one description that describes subject, action-pose-expression, hair-eyes-dress-accessories, and background in order using these keywords\n{inputs}"
]

with open("tag_lookup.txt", "r") as f:
    TAG_LOOKUP = dict(line.strip().split("%") for line in f)

with open(TAG_JSON_DIR, "r") as f:
    data = json.load(f)


def main():
    with open(TAG_JSON_DIR, "r") as f:
        data = json.load(f)

    # openai.api_key = OPENAI_API_KEY
    # captioned_data = make_data_multithread(data[:5])
    # with open("captioned_data.json", "w") as outfile:
    #     json.dump(captioned_data, outfile, indent=4)


def replace_general_tags(tags):
    return ' '.join([TAG_LOOKUP.get(x, x) for x in tags.split(' ')])


def generate_inputs(data_point) -> str:
    tag_string_general = replace_general_tags(data_point["tag_string_general"])
    tag_string_artist = data_point["tag_string_artist"]
    tag_string_copyright = data_point["tag_string_copyright"]
    tag_string_character = data_point["tag_string_character"]
    tag_string_meta = data_point["tag_string_meta"]

    return (
        "artist: " + tag_string_artist + "\n" +
        "character: " + tag_string_character + "\n" +
        "copyright: " + tag_string_copyright + "\n" +
        "general: " + tag_string_general + "\n"
        + "metadata: " + tag_string_meta + "\n"
    )


def generate_prompt(inputs: str, prompt_format: Union[str, int] = "random") -> str:

    if type(prompt_format) != str:
        prompt = PROMPT_FORMATS[prompt_format].format(inputs=inputs)
    else:
        prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    return prompt


inputs = generate_inputs(data[2])
print(generate_prompt(inputs, 3))


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


def make_data(data_point, prompt_format: str = "random") -> dict:
    inputs = generate_inputs(data_point)
    prompt = generate_prompt(inputs, prompt_format)
    caption = generate_caption(prompt)

    # Add the inputs, prompt, and caption strings to the data_point dictionary
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
