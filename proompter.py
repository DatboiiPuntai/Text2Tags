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
    "Write a caption with a highly neutral and objective tone using all the details from these Danbooru tags as keywords in under 200 words.\n {inputs}",
    "Write a concise and objective description for an illustration using the given keywords in under 200 words: {inputs}",
    "Describe a scene very objectively using these Danbooru tags as keywords in under 200 words.\n {inputs}",
]
LONG_PROMPT_FORMATS = [
    "Write a complete and objective description for an anime illustration using all the given keywords: {inputs}"
]

# To sort pprint(dict(sorted(TAG_TRANSLATION_LOOKUP.items())))
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
    # messages = [{"role": "user", "content": prompt}]
    # response = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=messages,
    #     temperature=TEMPERATURE,
    # )
    # caption = response["choices"][0]["message"]["content"]
    # return caption


def get_captions_multithread(data):
    threads = min(MAX_THREADS, len(data))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        captions = executor.map(get_caption, data)
    return list(captions)


captions = get_captions_multithread(data[:5])

# # sample 5 captions
# ["In this high-res artwork from Tokyo Afterschool Summoners, the blackcatlandr master 2 is flanked by a muscular male and a skirt-wearing girl, all with animal ears and horns. With brown hair, forked eyebrows, and glowing fiery horns, the trio's happy aura is palpable as they hug cheek-to-cheek, heads together with a single tear and teardrop. The cow boy with cow ears, cow horns, and eye black also joins in, sporting a goatee and facial hair. The spiky-haired boy in a gakuran and loafers stands nearby, while the simple background and thick eyebrows complete the scene. This image is sure to garner attention with its unique characters and Chinese commentary.", 
# 'This artwork is an official art featuring three girls from Hololive Indonesia: Anya Melfissa, Kureiji Ollie, and Pavolia Reine. They are all standing and looking at the viewer with smiles on their faces. Anya has long brown hair styled in a flower braid with ankle ribbon and is wearing a blue dress with ankle boots. Kureiji Ollie, with green eyes and purple tongue, has grey hair with streaks and is wearing a two-tone dress with sandals. Pavolia Reine has pink hair styled in looped braids with a blue bow and is wearing a see-through dress with ankle strap and toeless footwear. The artwork has a simple white background and all three girls are wearing white gloves. The tags also mention the presence of ankle strap, ankle ribbon, ankle boots, leg ribbon, and toeless footwear. Additionally, there are some unique features like the diamond-shaped pupils, heterochromia, and x-shaped pupils. There are also some elements indicating that they are virtual YouTubers like the copyright tag, index finger raised, and own hands together. Finally, the tags suggest that there are some stitched body parts like stitched arm, stitched face, and stitched leg, which may indicate that they are zombie characters.', 
# 'In the scene, a brother and sister duo from the game Fire Emblem Fates, Leo and Camilla, stand on a simple white background, looking straight at the viewer. Camilla, with her long blonde hair, is dressed in a flowing purple dress and wears thigh-highs and high heels. She holds a sword in one hand and a red rose in the other. Her hair drapes over one eye, emphasizing her beauty. Leo, with short red hair, wears traditional Japanese clothes and holds a weapon made of a leaf. A red flower sits in his hair as he stands beside his sister. The high-resolution image captures the intricate details of their outfits and weapons, making it absurdly clear.', 
# 'In this scene, a blonde-haired girl with blue eyes is sitting in a simple green background. She wears a white sailor dress with blue collar and puffy short sleeves, paired with white thigh-highs. Her fox ears and tail suggest she is a fox girl, and her animal ear fluff adds to her cuteness. She holds a paintbrush and looks at the viewer with one eye closed, her tongue sticking out playfully. Her collarbone is visible and she has a slight blush on her cheeks. The image is framed with a white border with a blue outside border. The artist, Manabe Mana, is credited.', 
# 'In a wintry landscape, a lone girl clad in armor stands before a group of boys. She wears a breastplate, gloves, and a helmet, with short blonde hair and striking green eyes. The boys surrounding her are also armored, with one identified as Satsuki (Chaosmode). Snowflakes drift down from the sky, settling on the bare trees and waving branches. The girl, identified as Lavian Windslet, gazes directly at the viewer as the scene unfolds. It is unclear what conflict has brought these warriors together, but the tag "Sen no Kiseki: Northern War" suggests a battle of some kind.']
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
