import editdistance
import re
import os


def correct_tags(tags, tag_dictionary):
    tags = (preprocess_tag(x) for x in tags)

    corrected_set = set()
    for tag in tags:
        threshold = max(1, len(tag)-10)
        closest = find_closest_tag(tag, threshold, tag_dictionary)
        if closest:
            corrected_set.add(closest)
    return sorted(list(corrected_set))


def preprocess_tag(tag):
    tag = tag.lower()
    match = re.match(r'^([^()]*\([^()]*\))\s*.*$', tag)
    return match.group(1) if match else tag


def find_closest_tag(tag: str, threshold: int, tag_dictionary: list):
    results = ((editdistance.eval(tag, x), x)
               for x in tag_dictionary)
    closest = sorted(results)[0]
    if closest[0] <= threshold:
        return closest[1]
    else:
        return None

def load_dict(path=os.path.join('dictionaries', 'tag_dict.txt')):
    with open(path, 'r') as f:
        tag_dict = f.read().splitlines()
    return tag_dict


def main():
    with open(os.path.join('dictionaries', 'tag_dict.txt'), 'r') as f:
        tag_dict = f.read().splitlines()

    tags = '___, bad_id, bad_pixiv_id, bangs, braid, breasts, brown_hair, closed_eyes, commentary_request, eyebrows_visible_through_hair, food, hairband, holding, holding_can, holding_can, hololive, long_hair, minato_aqua_(hololive), multiple_views, open_mouth, pink_hair, pink_shirt, shirt, sitting, solo, standing, twitter_username, twintails, upper_body, white_legwear, white_shirt, yellow_eyes, zettai_ryouiki_kiri, yuri_(yuri-mio)_(kyuu_nyuu)'
    print(tags)
    print(correct_tags(tags.split(', '), tag_dict))


if __name__ == '__main__':
    main()
