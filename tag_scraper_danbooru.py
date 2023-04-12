from bs4 import BeautifulSoup
import requests
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

POST_URL_TEMPLATE = "https://danbooru.donmai.us/posts/{id}"

MAX_THREADS = 12
DATA_FILE = "tag_data_danbooru.json"
NUM_IMAGES = 10000  # each page has 20 images


def main():
    print(f'Scraping tags from {NUM_IMAGES} random images on danbooru')
    urls = generate_urls(NUM_IMAGES, lower=3000000)
    data = make_data(urls)
    with open(DATA_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)


def has_picture_tag(url: str) -> bool:
    """
    Checks if the given URL contains a '<picture>' tag in its HTML response.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL contains a '<picture>' tag in its HTML response, False otherwise.
    """
    response = requests.get(url)
    pattern = re.compile(r"<picture>")
    return bool(pattern.search(response.text))


def generate_url(lower: int, upper: int) -> str:
    """
    Generates a single valid image URL from the Danbooru image board.

    Args:
        lower (int): The lower bound for the post ID.
        upper (int): The upper bound for the post ID.

    Returns:
        str: A valid image URL.
    """

    url = POST_URL_TEMPLATE.format(id=random.randint(lower, upper))
    if has_picture_tag(url):
        return url

    return None


def generate_urls(n: int, lower=1, upper=6219831) -> list[str]:
    """
    Generates a list of n valid image URLs from the Danbooru image board.

    Args:
        n (int): The number of URLs to generate.
        lower (int, optional): The lower bound for the post ID. Defaults to 1.
        upper (int, optional): The upper bound for the post ID. Defaults to 6219831.

    Returns:
        list[str]: A list of n valid image URLs.
    """
    url_list = []
    while len(url_list) < n:
        max_workers = min(n - len(url_list), MAX_THREADS)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(generate_url, lower, upper): None for _ in range(n)
            }

            for future in as_completed(future_to_url):
                url = future.result()
                if url is not None:
                    url_list.append(url)
                    if len(url_list) >= n:
                        break

    return url_list


# start_time = time.time()
# urls = generate_urls(1000, 3000000)
# end_time = time.time()
# print(f"Generated {len(urls)} URLs in {end_time - start_time} seconds.")


def get_tags_from_class(soup, tag_class) -> list[str]:
    """
    Given a BeautifulSoup object and a class name, return a list of tags
    with that class name.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object to search.
        tag_class (str): The class name of the tags to find.

    Returns:
        list: A list of BeautifulSoup tag objects with the given class name.
    """
    tag_list = soup.find("ul", {"class": tag_class})
    if tag_list:
        return list(map(lambda n: n.attrs["data-tag-name"], tag_list.find_all("li")))
    else:
        return []


def get_data_from_url(url: str) -> dict:
    """
    This function takes a URL string as input and returns a dictionary containing various data obtained from the Danbooru post located at the input URL.

    Parameters:
    url (str): A string containing the URL of the webpage to be scraped.

    Returns:
    dict: A dictionary containing various data obtained from the webpage located at the input URL. The keys in the dictionary are:
        - id: An integer ID extracted from the input URL.
        - artist: A list of strings containing the names of artists associated with the content on the webpage.
        - copyright: A list of strings containing any copyright information associated with the content on the webpage.
        - character: A list of strings containing the names of characters associated with the content on the webpage.
        - general: A list of strings containing any general tags associated with the content on the webpage.
        - metadata: A list of strings containing any metadata associated with the content on the webpage.
        - rating: A string containing the rating associated with the content on the webpage.
    """
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "lxml")

    artist_tags = get_tags_from_class(soup, "artist-tag-list")
    copyright_tags = get_tags_from_class(soup, "copyright-tag-list")
    character_tags = get_tags_from_class(soup, "character-tag-list")
    general_tags = get_tags_from_class(soup, "general-tag-list")
    metadata_tags = get_tags_from_class(soup, "meta-tag-list")

    id = int(url.split("/")[-1])
    rating = soup.find("li", {"id": "post-info-rating"}).text.split(" ")[-1]

    return_dict = {
        "id": id,
        "copyright": copyright_tags,
        "character": character_tags,
        "artist": artist_tags,
        "general": general_tags,
        "metadata": metadata_tags,

        "rating": rating,
    }
    return return_dict


# print(get_data_from_url("https://danbooru.donmai.us/posts/3053048"))


def make_data(urls: list[str]) -> list[dict]:
    """
    This function takes a list of URLs as input and returns a list of dictionaries containing data obtained by scraping danbooru for each URL in the input list.

    Parameters:
    urls (list[str]): A list of strings containing the URLs of the danbooru webpages to be scraped.

    Returns:
    list[dict]: A list of dictionaries containing various data obtained from each danbooru webpage in the input list. Each dictionary in the list corresponds to a single webpage and contains the following keys:
        - id: An integer ID extracted from the URL of the webpage.
        - artist: A list of strings containing the names of artists associated with the content on the webpage.
        - copyright: A list of strings containing any copyright information associated with the content on the webpage.
        - character: A list of strings containing the names of characters associated with the content on the webpage.
        - general: A list of strings containing any general tags associated with the content on the webpage.
        - metadata: A list of strings containing any metadata associated with the content on the webpage.
        - rating: A string containing the rating associated with the content on the webpage.
    """
    threads = min(MAX_THREADS, len(urls))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        data = executor.map(get_data_from_url, urls)
    return list(data)


if __name__ == "__main__":
    main()
