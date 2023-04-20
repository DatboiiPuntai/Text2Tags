import os
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import openai

DATA_FILE = r"dataset\danbooru2021posts.json"
OUTPUT_FILE = r"data_captioned.json"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.6
MAX_THREADS = 12
BATCH_SIZE = 50

# list of prompt formats to use for generating captions
PROMPT_TEMPLATES = [
    "Reply with an eloquent caption based on all the keywords.\n{inputs}",
    "Reply with a concise description of an artwork based on these keywords. Do not infer anything.\n{inputs}",
    "Reply with a highly condensed run on sentence that describe subject, action-pose-expression, hair-eyes-dress-accessories, and background in order using these keywords\n{inputs}",
]

with open("tag_lookup.txt", "r") as f:
    TAG_LOOKUP = dict(line.strip().split("%") for line in f)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    openai.api_key = os.getenv("OPENAI_API_KEY")

    data_with_captions = process_data(data)

    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(data_with_captions, outfile, indent=4)


def process_data(data):
    batches = [data[i : i + BATCH_SIZE] for i in range(0, len(data), BATCH_SIZE)]
    data_with_captions = []
    num_batch_errors = 0

    with tqdm(total=len(batches), desc="Processing batches") as pbar:
        for batch in batches:
            try:
                batch_with_captions = process_batch(batch)
                data_with_captions.extend(batch_with_captions)
                time.sleep(0.5)
                pbar.update(1)
            except:
                num_batch_errors += 1
                print(f"Error processing batch. Moving on to next batch.")
                if num_batch_errors >= 10:
                    print(f"Encountered 10 errors. Writing data to file.")
                    break

    return data_with_captions


def process_batch(batch):
    threads = min(MAX_THREADS, len(batch))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        batch_with_captions = list(
            tqdm(executor.map(make_data, batch), total=len(batch))
        )
    return batch_with_captions


def replace_general_tags(tags):
    # replace tags in tag string with their general categories using lookup dictionary
    return " ".join([TAG_LOOKUP.get(x, x) for x in tags.split(" ")])


def generate_prompt(data_point, prompt_format) -> str:
    tag_string_general = replace_general_tags(data_point["tag_string_general"])
    tag_string_artist = data_point["tag_string_artist"]
    tag_string_copyright = data_point["tag_string_copyright"]
    tag_string_character = data_point["tag_string_character"]

    inputs = (
        "artist: "
        + tag_string_artist
        + "\n"
        + "character: "
        + tag_string_character
        + "\n"
        + "from: "
        + tag_string_copyright
        + "\n"
        + "description: "
        + tag_string_general
    )

    prompt = PROMPT_TEMPLATES[prompt_format].format(inputs=inputs)

    if data_point["rating"] == "e":
        prompt += "\nUse exact explicit words."

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


def make_data(data_point) -> dict:
    prompt_format_idx = random.randrange(1,3)
    prompt = generate_prompt(data_point, prompt_format_idx)
    for i in range(5):
        try:
            caption = generate_caption(prompt)
            break
        except:
            print(f"Error generating caption. Trying again ({i+1}/5)")
            time.sleep(1)
    else:
        print("Error generating caption after 5 tries. Returning empty string.")
        caption = ""

    data_point["prompt_string"] = prompt
    data_point["prompt_format_id"] = prompt_format_idx
    data_point["caption_string"] = caption

    return data_point


if __name__ == "__main__":
    main()
