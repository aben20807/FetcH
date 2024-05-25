# FetcH

## Usage

```bash
$ python3 fetch.py --help
usage: FetcH [-h] [--dir DIR] url

Fetch HackMD bookmode files

positional arguments:
  url         Root URL of HackMD bookmode

options:
  -h, --help  show this help message and exit
  --dir DIR   Output directory

Author: Po-Hsuan Huang (aben20807)
```

## With curl

```bash
curl -s https://raw.githubusercontent.com/aben20807/FetcH/master/fetch.py | python3 - <your hackmd bookmode url>
```

## Example

```bash
$ curl -s https://raw.githubusercontent.com/aben20807/FetcH/master/fetch.py | python3 - https://hackmd.io/@docs/tutorials-tw
00-HackMD-使用教學.md
01-HackMD-Tutorial-Book.md
02-HackMD-使用教學.md
03-註冊與綁定.md
04-工作模式與快捷功能.md
05-如何編輯筆記的詮釋資料.md
06-加上或編輯標題.md
07-檢視.md
08-你知道-HackMD-是座大寶山嗎？.md
09-如何追蹤.md
10-手機如何編輯？.md
11-HackMD-快速入門教學.md
12-功能介紹.md
13-基本排版：標題、引用、粗體.md
14-螢光筆、色塊強調和收合功能.md
15-讓你的筆記更豐富-圖片上傳.md
16-使用-`{}`-嵌入外部的連結或部件.md
No filename found. Using default name.
17.md
18-讓筆記更活潑？加上-Emoji-吧.md
...
```
