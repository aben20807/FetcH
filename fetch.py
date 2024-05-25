import argparse
import requests
import re
import os

from urllib.parse import unquote


file_counter = 0


def get_filename(response, width):
    global file_counter
    filename = f"{file_counter:0{width}}"
    file_counter += 1
    try:
        find_filename = re.search(
            r'filename="(.*)"', response.headers["Content-Disposition"]
        )
    except KeyError:
        find_filename = False
    if find_filename:
        filename += "-" + unquote(find_filename.group(1)).replace(" ", "-")
    else:
        print("No filename found. Using default name.")
        filename += ".md"
    return filename


def get_args():
    parser = argparse.ArgumentParser(
        prog="FetcH",
        description="Fetch HackMD bookmode files",
        epilog="Author: Po-Hsuan Huang (aben20807)",
    )
    parser.add_argument("url", type=str, help="Root URL of HackMD bookmode")
    parser.add_argument("--dir", type=str, default="docs/", help="Output directory")
    return parser.parse_args()


def main():
    args = get_args()

    root_url = args.url
    root_dir = args.dir

    # Fetch root
    root_response = requests.get(root_url + "/download")

    # Get hackmd urls
    hackmd_urls = []
    root_content = root_response.text
    for line in root_content.split("\n"):
        find_hackmd_url = re.search(r"\((https://hackmd.io/.*)\)", line)
        if find_hackmd_url:
            hackmd_urls.append(find_hackmd_url.group(1))
            continue
        find_hackmd_url = re.search(r"\(/(.*)\)", line)
        if find_hackmd_url:
            hackmd_urls.append("https://hackmd.io/" + find_hackmd_url.group(1))
            continue

    # Make the width of the prefix index
    width = len(str(len(hackmd_urls) + 1))
    root_filename = get_filename(root_response, width)
    print(root_filename)

    # Write root file
    os.makedirs(root_dir, exist_ok=True)
    with open(root_dir + root_filename, "w", encoding="utf-8") as root_file:
        root_file.write(root_content)

    # Fetch and write files
    for hackmd_url in hackmd_urls:
        hackmd_response = requests.get(hackmd_url + "/download")
        hackmd_content = hackmd_response.text
        hackmd_filename = get_filename(hackmd_response, width)
        print(hackmd_filename)
        with open(root_dir + hackmd_filename, "w", encoding="utf-8") as hackmd_file:
            hackmd_file.write(hackmd_content)


if __name__ == "__main__":
    main()
