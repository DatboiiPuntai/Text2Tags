import os
import json
import random
from itertools import chain
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from typing import Union
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAG_JSON_DIR = r"dataset\tag_data.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7
MAX_THREADS = 10

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


def main():
    with open(TAG_JSON_DIR, "r") as f:
        data = json.load(f)

    openai.api_key = OPENAI_API_KEY
    captioned_data = make_data_multithread(data[:5])
    with open("captioned_data.json", "w") as outfile:
        json.dump(captioned_data, outfile, indent=4)


def replace_tags(tags: list[str]) -> list[str]:
    """
    Given a list of general tags, this function returns a new list of tags where each
    general tag has been translated using a lookup table. If a tag is not found in the
    lookup table, it is left unchanged.

    Args:
        general_tags (List[str]): A list of strings representing general tags.

    Returns:
        List[str]: A new list of strings where each general tag has been replaced with
        its translation, if one exists in the lookup table.
    """
    tags_translated = [TAG_TRANSLATION_LOOKUP.get(x, x) for x in tags]
    return tags_translated


# print(replace_tags([';d','^^^','bruh']))


def flatten_to_string_input(data_point: dict[str, list[str]]) -> str:
    """
    Given a dictionary `data_point` containing keys for "copyright",
    "character", "artist", "general", and "metadata", this function returns
    a string representation of the values associated with those keys.

    The values are joined together into a single string, with each value separated
    by a comma and space.

    Args:
        data_point (Dict[str, List[str]]): A dictionary containing keys for
        "copyright", "character", "artist", "general", and "metadata".

    Returns:
        str: A string representation of the values associated with the keys in
        `data_point`, joined together with a comma and space.
    """
    keys = ("copyright", "character", "artist", "general", "metadata")
    flattened_values = list(chain.from_iterable([data_point[x] for x in keys]))
    return ", ".join(flattened_values)


# print(flatten_to_string_input(data[0]))


def get_prompt(inputs: str, prompt_format: Union[str, int] = "random") -> str:
    """
    Given a string `inputs`, this function returns a prompt that can be used to ask a question
    or solicit additional information about the inputs.

    If the length of `inputs` is greater than 1200, a long prompt format is used. Otherwise,
    a prompt format is selected based on the `prompt_format` argument.

    Args:
        inputs (str): A string containing the input data to generate a prompt for.
        prompt_format (Union[str, int], optional): The format to use for the prompt. Can be
            one of "random" (default), which selects a random prompt format from `PROMPT_FORMATS`,
            or an integer index into `PROMPT_FORMATS`, specifying a specific prompt format to use.

    Returns:
        str: A prompt string generated based on the input `inputs` and the `prompt_format`.

    Raises:
        IndexError: If `prompt_format` is an integer index that is out of range for `PROMPT_FORMATS`.
    """
    if len(inputs) > 1200:
        prompt = LONG_PROMPT_FORMATS[0].format(inputs=inputs)
    else:
        if type(prompt_format) != str:
            prompt = PROMPT_FORMATS[prompt_format].format(inputs=inputs)
        else:
            prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    return prompt


def get_caption(prompt: str) -> str:
    """
    Given a prompt string, generates a caption using OpenAI's GPT-3 language model.

    Args:
        prompt (str): A string prompt to use as input for the GPT-3 model.

    Returns:
        str: The generated caption string.
    """
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
    """
    Given a dictionary `data_point`, generates inputs, prompt, and caption strings using OpenAI's GPT-3 language model.

    Args:
        data_point (dict): A dictionary containing various keys, including "copyright",
            "character", "artist", "general", and "metadata", each with a list value.
            The function uses the "general" list to generate inputs for the GPT-3 model.

        prompt_format (str, optional): The format to use for the prompt. Defaults to "random".

    Returns:
        dict: A modified version of the `data_point` dictionary with added "inputs", "prompt", and "caption" keys
            and their corresponding values.
    """
    # Create a copy of the data_point dictionary to avoid modifying the original
    data_point_modified = data_point.copy()

    # Replace general tags in the "general" list using a helper function
    data_point_modified["general"] = replace_tags(data_point["general"])

    # Flatten the modified data_point dictionary to a string input using a helper function
    inputs = flatten_to_string_input(data_point_modified)

    # Generate a prompt string using a helper function
    prompt = get_prompt(inputs, prompt_format)

    # Generate a caption string using a helper function
    caption = get_caption(prompt)

    # Add the inputs, prompt, and caption strings to the data_point dictionary
    data_point["inputs"] = inputs
    data_point["prompt"] = prompt
    data_point["caption"] = caption

    # Return the modified data_point dictionary
    return data_point
data_point = {
    "copyright":[],
    "character": [],
        "artist": [
            "ai-wa"
        ],
        "general": [
            "1girl",
            "pussy",
            "mosaic censoring",
            "cowgirl position",
            "interlocked fingers"
        ],
        "metadata": [
            "absurdres"
        ],
}
print(make_data(data_point))

def make_data_multithread(data):
    threads = min(MAX_THREADS, len(data))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        captioned_data = executor.map(make_data, data)
    return list(captioned_data)


# if __name__ == "__main__":
#     main()
