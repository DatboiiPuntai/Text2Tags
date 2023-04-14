from bs4 import BeautifulSoup
import requests
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
import json

POST_URL_TEMPLATE = "https://danbooru.donmai.us/posts/{id}"

DATA_FILE = "tag_data_danbooru.json"
NUM_IMAGES = 15000

### Random post sampling
LOWER_BOUND = 3000000
UPPER_BOUND = 6221657


def main():
    post_ids = list(range(LOWER_BOUND, UPPER_BOUND + 1))
    random.shuffle(post_ids)

    data = []

    while len(data) < NUM_IMAGES:
        url = POST_URL_TEMPLATE.format(id=post_ids.pop())
        soup = get_soup(url)
        data_point = parse_data(soup)
        if data_point:
            data.append(data_point)

    with open(DATA_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    return soup


def get_tags_from_category(soup, tag_class):
    category = soup.find("ul", {"class": tag_class})
    return (
        [x.attrs["data-tag-name"] for x in category.find_all("li")]
        if category
        else None
    )


def parse_data(soup):
    sidebar = soup.find("aside", {"id": "sidebar"})

    if not sidebar:
        return None

    return {
        "id": soup.find("li", {"id": "post-info-id"}).text.split(": ")[-1],
        "rating": soup.find("li", {"id": "post-info-rating"}).text.split(": ")[-1],
        "tags": {
            "artist": get_tags_from_category(soup, "artist-tag-list"),
            "copyright": get_tags_from_category(soup, "copyright-tag-list"),
            "character": get_tags_from_category(soup, "character-tag-list"),
            "general": get_tags_from_category(soup, "general-tag-list"),
            "metadata": get_tags_from_category(soup, "meta-tag-list"),
        },
    }


if __name__ == "__main__":
    main()
