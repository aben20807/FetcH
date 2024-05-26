import argparse
import multiprocessing
import os
import requests
import re

from urllib.parse import unquote


def get_filename(response, index, width):
    filename = f"{index:0{width}}"
    try:
        find_filename = re.search(
            r'filename="(.*)"', response.headers["Content-Disposition"]
        )
    except KeyError:
        find_filename = False
    if find_filename:
        filename += "-" + unquote(find_filename.group(1)).replace(" ", "-")
    else:
        print("[WARN] No filename found. Using default name.")
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


def worker(hackmd_url, root_dir, index, width):
    hackmd_response = requests.get(hackmd_url + "/download")
    if hackmd_response.status_code == 403:
        print(
            f"[ERROR] 403 Forbidden: `{hackmd_url}`. You may need to change the share configuration."
        )
        return
    if hackmd_response.status_code != 200:
        print(f"[ERROR] Unknown error for downloading `{hackmd_url}`.")
        return
    hackmd_content = hackmd_response.text
    hackmd_filename = get_filename(hackmd_response, index, width)
    print(f"[INFO] {hackmd_filename}")
    with open(root_dir + hackmd_filename, "w", encoding="utf-8") as hackmd_file:
        hackmd_file.write(hackmd_content)


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
    root_filename = get_filename(root_response, 0, width)
    print(f"[INFO] {root_filename}")

    # Write root file
    os.makedirs(root_dir, exist_ok=True)
    with open(root_dir + root_filename, "w", encoding="utf-8") as root_file:
        root_file.write(root_content)

    # Fetch and write files
    with multiprocessing.Pool() as pool:
        pool.starmap(
            worker,
            [
                (hackmd_url, root_dir, index + 1, width)
                for index, hackmd_url in enumerate(hackmd_urls)
            ],
        )


if __name__ == "__main__":
    main()
