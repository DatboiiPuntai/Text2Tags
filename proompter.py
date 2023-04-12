import os
import json
import random
from itertools import chain
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAG_JSON_DIR = r"dataset\tag_data.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7
MAX_THREADS = 10

PROMPT_FORMATS = [
    "Write a caption with a highly neutral and objective tone using ALL the details from these Danbooru tags as keywords including the artist in under 200 words {inputs}",
    "Describe an anime illustration with a dry tone using all details from these Danbooru tags as keywords including the artist in about 200 words {inputs}",
    "Write a concise but detailed caption using the following keywords: {inputs}",
    "Describe a scene dryly using these Danbooru tags as keywords. Emphasize Japanese terms if present. {inputs}",
    "Describe an artwork in a matter-of-fact tone using these Danbooru tags as keywords. {inputs}",
]

# To sort this pprint(dict(sorted(TAG_TRANSLATION_LOOKUP.items())))
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

with open(TAG_JSON_DIR, "r") as f:
    data = json.load(f)
openai.api_key = OPENAI_API_KEY


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


def get_caption(data_point):
    data_point_translated = replace_tags(data_point)
    inputs = flatten_to_string_input(data_point_translated)
    prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    print(f'{prompt=}')
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
    )
    caption = response["choices"][0]["message"]["content"]
    return caption


print(get_caption(data_point=data[5]))

# sample response
# response = {
#     "choices": [
#         {
#             "finish_reason": "stop",
#             "index": 0,
#             "message": {
#                 "content": "In this high-resolution image, we see a lone minigirl dressed in a blue pinafore dress displaying an Alice-in-Wonderland theme. The girl, bearing the name 'Alice,' has long blonde hair tied into a bow and worn with a black hairband. She also wears a blue bow on her head and green eyes that match the scenes' grassy background. Alice has on white socks with frilled cuffs that match her sleeveless dress's puffy short sleeves. She also sports wrist cuffs and hair between her eyes, emphasizing her heterochromia. While standing in the grass, Alice can be seen eating and sitting near a mushroom and a snail. With her feet out of the frame and a closed mouth, Alice looks focused, but her eyes give a subtle hint of wonder. Overall, the outfit is completed with frills and a hair bow, making it a perfect depiction of Alice in Wonderla nd.",
#                 "role": "assistant",
#             },
#         }
#     ],
#     "created": 1681278502,
#     "id": "chatcmpl-74Nd8eJxogZfLdzjeAC6H11vXsZun",
#     "model": "gpt-3.5-turbo-0301",
#     "object": "chat.completion",
#     "usage": {"completion_tokens": 188, "prompt_tokens": 188, "total_tokens": 376},
# }
