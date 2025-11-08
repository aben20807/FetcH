import argparse
import multiprocessing
import os
import re
import time
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session_with_retries(retries=3, backoff_factor=0.5):
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 504),
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


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
        print("[WARN] No filename found. Using default name.", flush=True)
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
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            session = get_session_with_retries()
            hackmd_response = session.get(hackmd_url + "/download", timeout=30)
            
            if hackmd_response.status_code == 403:
                print(
                    f"[ERROR] 403 Forbidden: {hackmd_url} You may need to change the share configuration.",
                    flush=True,
                )
                return
            if hackmd_response.status_code != 200:
                print(f"[ERROR] Status {hackmd_response.status_code} for downloading {hackmd_url}", flush=True)
                return
            
            hackmd_content = hackmd_response.text
            hackmd_filename = get_filename(hackmd_response, index, width)
            print(f"[INFO] {hackmd_filename}", flush=True)
            
            with open(root_dir + hackmd_filename, "w", encoding="utf-8") as hackmd_file:
                hackmd_file.write(hackmd_content)
            return  # Success, exit function
            
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            if attempt < max_retries - 1:
                print(
                    f"[WARN] Attempt {attempt + 1}/{max_retries} failed for {hackmd_url}: {str(e)}. Retrying in {retry_delay}s...",
                    flush=True,
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(
                    f"[ERROR] Failed to download {hackmd_url} after {max_retries} attempts: {str(e)}",
                    flush=True,
                )
                return
        except Exception as e:
            print(f"[ERROR] Unexpected error for {hackmd_url}: {str(e)}", flush=True)
            return


def main():
    args = get_args()

    root_url = args.url
    root_dir = args.dir

    # Fetch root with retry logic
    try:
        session = get_session_with_retries()
        root_response = session.get(root_url + "/download", timeout=30)
        root_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch root URL {root_url}: {str(e)}", flush=True)
        return

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
    print(f"[INFO] {root_filename}", flush=True)

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
