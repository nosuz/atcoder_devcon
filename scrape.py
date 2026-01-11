#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# -----------------------------
# HTML ダウンロード
# -----------------------------


def download_html(url: str, cookies: dict[str, str] | None = None, wait: int = 3) -> str:
    """
    Cookie を使って Web ページをダウンロードする
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    # make a break between requests
    time.sleep(wait)
    resp = requests.get(url, cookies=cookies, headers=headers, timeout=10)
    resp.raise_for_status()

    return resp.text

# -----------------------------
# HTML 解析：入力例・出力例抽出
# -----------------------------


def extract_examples_from_html(html: str):
    """
    AtCoder 問題ページの HTML から
    入力例・出力例を抽出する

    return:
      [
        { "input": "...\\n", "output": "...\\n" },
        ...
      ]
    """
    soup = BeautifulSoup(html, "html.parser")
    parts = soup.select("div.part")

    examples = []
    i = 0
    while i < len(parts):
        h3_in = parts[i].find("h3")
        pre_in = parts[i].find("pre")

        if h3_in and "入力例" in h3_in.text and pre_in:
            if i + 1 < len(parts):
                h3_out = parts[i + 1].find("h3")
                pre_out = parts[i + 1].find("pre")

                if h3_out and "出力例" in h3_out.text and pre_out:
                    examples.append({
                        "input": pre_in.text.replace("\r", ""),
                        "output": pre_out.text.replace("\r", "")
                    })
                    i += 2
                    continue
        i += 1

    return examples


def extract_problem_title(html: str) -> str | None:
    """
    問題タイトルを取得する
    XPath:
      //*[@id="main-container"]/div[1]/div[2]/span[1]/text()
    に相当
    """
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find(id="main-container")
    if not container:
        return None

    span = container.select_one("div.row > div.col-sm-12 > span.h2")
    if not span:
        return None

    # span.h2 の直下テキストのみを取得（Editorial を除外）
    title = span.find(string=True, recursive=False)
    if title:
        return title.strip()

    return None

# -----------------------------
# HTML 解析：コンテストメタ情報抽出
# -----------------------------


def extract_contest_meta_from_html(html: str) -> dict:
    """
    AtCoder コンテストページ(または問題ページ)の HTML から
    コンテストのメタ情報を抽出する。

    - title: 例 "AtCoder Beginner Contest 438"
    - start_time_raw: 例 "2025-12-27 21:00:00+0900"
    - date: README 用に人間が読みやすい形式（例 "2025-12-27" や "2025 年 12 月 27 日"）
    """
    soup = BeautifulSoup(html, "html.parser")

    # タイトル: 問題ページでは navbar の a.contest-title が取りやすい
    title_el = soup.select_one("a.contest-title")
    if not title_el:
        # コンテストトップでは h1 がある場合もあるのでフォールバック
        title_el = soup.select_one("#main-container h1")
    title = title_el.get_text(strip=True) if title_el else None

    # 開催日時: ユーザー指定 selector
    time_el = soup.select_one(
        "#contest-nav-tabs > div > small.contest-duration > a:nth-child(1) > time"
    )
    start_time_raw = time_el.get_text(strip=True) if time_el else None

    # README 用の日付（多少崩れても落ちないように）
    date_str = None
    if start_time_raw:
        # 例: "2025-12-27 21:00:00+0900"
        for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(start_time_raw, fmt)
                date_str = dt.strftime("%Y-%m-%d")
                break
            except Exception:
                pass
        if not date_str:
            # パースできない場合は先頭 10 文字だけでも日付っぽくする
            date_str = start_time_raw[:10]

    return {
        "title": title,
        "start_time_raw": start_time_raw,
        "date": date_str,
    }


# -----------------------------
# キャッシュ管理（contest）
# -----------------------------


def _contest_cache_path(base_dir):
    return os.path.join(base_dir, "cache", "contest.json")


def load_contest_cache(base_dir):
    path = _contest_cache_path(base_dir)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_contest_cache(base_dir, url: str, meta: dict):
    cache_dir = os.path.join(base_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    data = {
        "url": url,
        **meta,
    }
    with open(_contest_cache_path(base_dir), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# キャッシュ管理
# -----------------------------


def _cache_path(base_dir, problem):
    return os.path.join(base_dir, "cache", f"{problem}.json")


def load_cache(base_dir, problem):
    """
    キャッシュが存在すれば読み込む
    """
    path = _cache_path(base_dir, problem)
    if not os.path.exists(path):
        return None

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_cache(base_dir, problem, url, title, examples):
    cache_dir = os.path.join(base_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)

    data = {
        "problem": problem,
        "title": title,
        "url": url,
        "examples": examples
    }

    with open(_cache_path(base_dir, problem), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------------
# .in / .out 形式で保存
# -----------------------------


def save_examples_as_inout(base_dir, problem, examples):
    """
    examples/A_1.in
    examples/A_1.out
    """
    example_dir = os.path.join(base_dir, "examples")
    os.makedirs(example_dir, exist_ok=True)

    for i, ex in enumerate(examples, 1):
        in_path = os.path.join(example_dir, f"{problem}_{i}.in")
        out_path = os.path.join(example_dir, f"{problem}_{i}.out")

        with open(in_path, "w", encoding="utf-8") as f:
            f.write(ex["input"])

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(ex["output"])


# -----------------------------
# 単体テスト用 CLI
# -----------------------------
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="scrape.py standalone test (offline HTML)"
    )
    parser.add_argument(
        "--html",
        required=True,
        help="HTML file of problem page"
    )
    parser.add_argument(
        "--out",
        default=".",
        help="output base directory"
    )
    parser.add_argument(
        "--problem",
        default="A",
        help="problem name (A, B, ...)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.html):
        print(f"❌ HTML file not found: {args.html}")
        sys.exit(1)

    with open(args.html, encoding="utf-8") as f:
        html = f.read()

    title = extract_problem_title(html)
    examples = extract_examples_from_html(html)

    print(f"✅ extracted {len(examples)} example(s)")

    for i, ex in enumerate(examples, 1):
        print(f"\n--- example {i} ---")
        print("INPUT:")
        print(ex["input"])
        print("OUTPUT:")
        print(ex["output"])

    save_examples_as_inout(args.out, args.problem, examples)
    print(f"\n📁 saved to {os.path.join(args.out, 'examples')}")
    save_cache(args.out, args.problem, None, title, examples)
