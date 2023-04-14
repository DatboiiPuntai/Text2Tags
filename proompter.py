import os
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import openai

TAG_JSON_DIR = r"dataset\danbooru2021posts.json"
OUTFILE = r"data_captioned.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.6
MAX_THREADS = 10
BATCH_SIZE = 50

# list of prompt formats to use for generating captions
PROMPT_FORMATS = [
    "Reply with a complete description of an artworkusing these keywords. Do not infer anything.\n{inputs}",
    "Using these keywords, reply with a creative and eloquent caption.\n{inputs}",
    "Reply with a short and summarized description of an artwork based on these keywords. Do not go over 75 words.\n{inputs}",
    "Reply with only one description that describes subject, action-pose-expression, hair-eyes-dress-accessories, and background in order using these keywords\n{inputs}",
]

with open("tag_lookup.txt", "r") as f:
    TAG_LOOKUP = dict(line.strip().split("%") for line in f)


def main():
    with open(TAG_JSON_DIR, "r", encoding="utf-8") as f:
        data = json.load(f)

    openai.api_key = os.getenv("OPENAI_API_KEY")

    batches = [data[i : i + BATCH_SIZE] for i in range(0, len(data), BATCH_SIZE)]

    captioned_data = []

    with tqdm(total=len(batches), desc="Processing batches") as pbar:
        for batch in batches:
            try:
                captioned_batch = process_batch(batch)
                captioned_data.extend(captioned_batch)
                time.sleep(1)
                pbar.update(1)
            except:
                print(f"Error processing batch. Moving on to next batch.")

    with open(OUTFILE, "w") as outfile:
        json.dump(captioned_data, outfile, indent=4)


def process_batch(batch):
    threads = min(MAX_THREADS, len(batch))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        captioned_batch = list(tqdm(executor.map(make_data, batch), total=len(batch)))
    return captioned_batch


def replace_general_tags(tags):
    # replace tags in tag string with their general categories using lookup dictionary
    return " ".join([TAG_LOOKUP.get(x, x) for x in tags.split(" ")])


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
        # + "metadata: " + tag_string_meta + "\n"
    )


def generate_prompt(inputs: str, prompt_format="random") -> str:
    if type(prompt_format) != str:
        prompt = PROMPT_FORMATS[prompt_format].format(inputs=inputs)
    else:
        prompt = random.choice(PROMPT_FORMATS).format(inputs=inputs)
    return prompt


def generate_caption(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
    )

    caption = response["choices"][0]["message"]["content"]
    return caption


def make_data(data_point, prompt_format="random") -> dict:
    inputs = generate_inputs(data_point)
    prompt = generate_prompt(inputs, prompt_format)
    caption = generate_caption(prompt)

    data_point["prompt"] = prompt
    data_point["caption"] = caption

    return data_point


if __name__ == "__main__":
    main()