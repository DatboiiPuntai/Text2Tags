from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
import json

POST_URL_TEMPLATE = "https://safebooru.org/index.php?page=post&s=view&id={id}"
SEARCH_URL_TEMPLATE = (
    "https://safebooru.org/index.php?page=post&s=list&tags={tags}&pid={pid}"
)

MAX_THREADS = 50
DATA_FILE = 'tag_data.json'
NUM_PAGES = 250 # each page has 40 posts

def main():
    print(f'Scraping tags from {NUM_PAGES * 40} images from safebooru')
    data = scrape(tags=["-tagme"], num_pages=NUM_PAGES)
    with open(DATA_FILE,'w') as outfile:
        json.dump(data, outfile, indent=4)
    

def get_ids_from_url(url: str) -> list[str]:
    """
    Returns a list of post ids found in the given url's html content

    Args:
    url(str): The url to search

    Returns:
    list: A list of post ids

    Example usage:
    url = SEARCH_URL_TEMPLATE.format(tags='-tagme',pid=0)
    print(get_ids_from_url(url))
    """
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "lxml")
    # Find all span elements with class "thumb", then get their "id" attribute (skipping the first character), which is the post ID
    span_elements = (
        soup.find("div", {"id": "content"})
        .find_all("div")[0]
        .find_all("span", {"class": "thumb"})
    )
    return [span.get("id")[1:] for span in span_elements]


def get_urls_from_tags(tag_list: list[str], num_pages=10) -> list[str]:
    """
    Given a list of tags and the number of pages to search, return a list of urls to search for images on safebooru.org.

    Args:
    - tag_list (list[str]): A list of tags to search for.
    - num_pages (int): The number of pages to search.

    Returns:
    - A list of urls to search for images on safebooru.org.

    Example usage:
    print(get_urls_from_tags(['-tagme', 'virtual_youtuber'])[1])
    """
    tags = "+".join(tag_list)
    return [SEARCH_URL_TEMPLATE.format(tags=tags, pid=i * 40) for i in range(num_pages)]


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
    lists = soup.find_all("li", {"class": tag_class})
    return [li.find("a").text for li in lists]


def get_url_from_id(id) -> str:
    return POST_URL_TEMPLATE.format(id=id)


def get_tags_from_url(url) -> dict:
    """
    Given a post url, return a dictionary of tags associated with the post.

    Args:
        url (str): The url of the post to scrape.

    Returns:
        dict: A dictionary with keys 'copyright', 'character', 'artist',
            'general', and 'metadata', where each key maps to a list of tags
            associated with the post.

    Example usage:
    url = POST_URL_TEMPLATE.format(id=4326735)
    print(get_tags_from_url(url))
    """
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "lxml")

    copyright_tags = get_tags_from_class(soup, "tag-type-copyright tag")
    character_tags = get_tags_from_class(soup, "tag-type-character tag")
    artist_tags = get_tags_from_class(soup, "tag-type-artist tag")
    general_tags = get_tags_from_class(soup, "tag-type-general tag")
    metadata_tags = get_tags_from_class(soup, "tag-type-metadata tag")

    return_dict = {
        "copyright": copyright_tags,
        "character": character_tags,
        "artist": artist_tags,
        "general": general_tags,
        "metadata": metadata_tags,
    }

    return return_dict


def get_ids_multithread(urls: list[str]) -> list[str]:
    """
    Returns a single flat list of post ids found in the given urls' html content,
    utilizing multithreading to improve performance.

    Args:
    - urls (list[str]): A list of urls to search for post ids.

    Returns:
    - A list of post ids found in the given urls' html content.

    Example usage:
    urls = get_urls_from_tags(['-tagme', 'virtual_youtuber'])
    print(get_ids_multithread(urls))
    """
    threads = min(MAX_THREADS, len(urls))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        ids_lists = executor.map(get_ids_from_url, urls)
    return list(chain.from_iterable(ids_lists))


def get_tags_multithread(urls: list[str]) -> list[dict]:
    """
    Given a list of urls, returns a list of dictionaries containing tags associated with each post.

    Args:
    urls (list[str]): A list of urls to search for the tags.

    Returns:
    A list of dictionaries, where each dictionary contains tags associated with a single post. Each dictionary has keys 'copyright',
    'character', 'artist', 'general', and 'metadata', where each key maps to a list of tags associated with the post.

    Example:
    >>> urls = ['https://example.com/post/4326735', 'https://example.com/post/4357947', 'https://example.com/post/4361438']
    >>> print(get_tags_multithread(urls))
    [{'copyright': [],
      'character': ['Alice', 'Bob'],
      'artist': ['artistA'],
      'general': ['example', 'artwork'],
      'metadata': []},
     {'copyright': ['among us 2 electric boogaloo],
      'character': ['Eve'],
      'artist': ['artistB'],
      'general': ['example', 'illustration'],
      'metadata': []},
     {'copyright': [],
      'character': ['Charlie'],
      'artist': ['artistC'],
      'general': ['example', 'drawing'],
      'metadata': []}]
    """
    threads = min(MAX_THREADS, len(urls))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        tags_list = executor.map(get_tags_from_url, urls)
    return list(tags_list)


def scrape(tags: list[str], num_pages: int):
    urls = get_urls_from_tags(tags, num_pages)
    ids = get_ids_multithread(urls)
    post_urls = list(map(get_url_from_id, ids))
    data = get_tags_multithread(post_urls)
    return data

if __name__ == "__main__":
    main()


