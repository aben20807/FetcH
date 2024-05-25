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

## Sync with github action

`.github/workflows/sync.yml`, remember to replace `<your hackmd bookmode url>`:

```yaml
name: Sync from HackMD

on:
  schedule: # execute every 24 hours
    - cron: "* */24 * * *"
  workflow_dispatch:
  push:
    branches:
      - master

jobs:
  sync:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}

      - name: Sync from HackMD
        run: |
          rm -r docs/
          curl -s https://raw.githubusercontent.com/aben20807/FetcH/master/fetch.py | python3 - https://hackmd.io/@aben20807/HyKAHCfg0

      - name: Retrieve commit message
        run: | # https://trstringer.com/github-actions-multiline-strings/
          CMT_MSG=$(cat << EOF
          Synced `date '+%Y-%m-%d %H:%M:%S %:::z'`
          EOF
          )
          echo "CMT_MSG<<EOF" >> $GITHUB_ENV
          echo "$CMT_MSG" >> $GITHUB_ENV
          echo "EOF" >> $GITHUB_ENV
        id: message

      - uses: stefanzweifel/git-auto-commit-action@v5
        id: auto-commit-action
        with:
          commit_message: ${{ env.CMT_MSG }}
      
      - name: "Run if no changes have been detected"
        if: steps.auto-commit-action.outputs.changes_detected == 'false'
        run: echo "No Changes!"
```

## License

MIT
