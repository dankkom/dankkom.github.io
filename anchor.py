import argparse
import re
from pathlib import Path
from pprint import pprint


def get_anchor_tags(text: str) -> str:
    anchors = re.findall(r"(<a[^>]*>([^<]+)<\/a>)", text)
    result = []
    for a in anchors:
        href = re.search(r'(?<=href=")[^"]*(?=")', a[0]).group()
        result.append(
            {
                "a": a,
                "text": a[1],
                "href": href,
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=Path, required=True)
    args = parser.parse_args()
    filepath = args.file

    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    for a in get_anchor_tags(text):
        print(f">> [{a['text']}]({a['href']})")
        text = text.replace(a["a"][0], f"[{a['text']}]({a['href']})")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
