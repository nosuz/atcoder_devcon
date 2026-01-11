#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import json
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scrape import (
    download_html,
    extract_problem_title,
    extract_examples_from_html,
    extract_contest_meta_from_html,
    load_cache,
    save_cache,
    load_contest_cache,
    save_contest_cache,
    save_examples_as_inout,
)

PROBLEMS = ["A", "B", "C", "D", "E", "F"]
SUPPORTED_LANGUAGES = ["java", "python"]


def contest_url(contest: str) -> str:
    return f"https://atcoder.jp/contests/{contest}"


def load_cookies(path="cookies.json"):
    if not os.path.exists(path):
        print("ℹ️ cookies.json not found (access as guest)")
        return None
    with open(path, encoding="utf-8") as f:
        print("🍪 cookies loaded")
        return json.load(f)


def task_url(contest: str, problem: str) -> str:
    return (
        f"https://atcoder.jp/contests/{contest}/tasks/"
        f"{contest}_{problem.lower()}"
    )


def scrape_contest(contest: str):
    """
    問題ページを scrape して cache / examples を作成
    """
    out_dir = contest.upper()
    os.makedirs(out_dir, exist_ok=True)

    cookies = load_cookies()

    # ---- contest meta (cached) ----
    ccache = load_contest_cache(out_dir)
    if ccache:
        print("⚡ contest meta cache hit")
        cmeta = ccache
    else:
        url = contest_url(contest)
        print(f"🌐 fetching contest page: {url}")
        html = download_html(url, cookies=cookies, wait=0)
        meta = extract_contest_meta_from_html(html)
        save_contest_cache(out_dir, url, meta)
        cmeta = {"url": url, **meta}

    # README 用に problems リストを作る（後でキャッシュから title/url を拾う）
    problems_for_readme = []

    for problem in PROBLEMS:
        print(f"\n=== Problem {problem} ===")

        cache = load_cache(out_dir, problem)
        if cache:
            print("⚡ cache hit")
            examples = cache["examples"]
            title = cache.get("title")
            url = cache.get("url")
        else:
            url = task_url(contest, problem)
            print(f"🌐 fetching: {url}")

            html = download_html(url, cookies=cookies)
            title = extract_problem_title(html)
            examples = extract_examples_from_html(html)

            print(f"📘 title: {title}")
            print(f"📄 examples: {len(examples)}")

            save_cache(out_dir, problem, url, title, examples)

        save_examples_as_inout(out_dir, problem, examples)

        problems_for_readme.append(
            {
                "id": problem,
                "title": title or f"Problem {problem}",
                "url": url or task_url(contest, problem),
            }
        )

    # ---- README.md ----
    tools_dir = Path(__file__).resolve().parent
    tmpl_dir = tools_dir / "templates"
    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    # templates/readme_template.md を想定（ユーザーが templates にまとめたい方針）
    t_readme = env.get_template("readme_template.md")

    readme_contents = {
        "contest": cmeta.get("title") or contest.upper(),
        "date": cmeta.get("date") or cmeta.get("start_time_raw") or "",
        "url": cmeta.get("url") or contest_url(contest),
        "problems": problems_for_readme,
    }
    readme_path = Path(out_dir) / "README.md"
    readme_path.write_text(
        t_readme.render(contents=readme_contents),
        encoding="utf-8",
    )
    print(f"\n📝 README generated: {readme_path}")

    print("\n✅ scrape finished successfully")


def _jinja_env() -> Environment:
    tools_dir = Path(__file__).resolve().parent
    tmpl_dir = tools_dir / "templates"
    return Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )


def _render_template(name: str, *, contest: str) -> str:
    env = _jinja_env()
    t = env.get_template(name)
    return t.render(content={"contest": contest}, problems=PROBLEMS)


def _append_block_if_missing(
    gitignore_path: Path,
    marker: str,
    block_text: str,
) -> bool:
    txt = gitignore_path.read_text(encoding="utf-8")

    start_marker = f"# <<< {marker} >>>"
    if start_marker in txt:
        return False  # すでにある

    if not txt.endswith("\n"):
        txt += "\n"
    if not txt.endswith("\n\n"):
        txt += "\n"

    gitignore_path.write_text(txt + block_text, encoding="utf-8")
    return True


def ensure_gitignore_split(contest: str, languages: list[str]) -> None:
    contest_dir = Path(contest.upper())
    contest_dir.mkdir(parents=True, exist_ok=True)

    gitignore_path = contest_dir / ".gitignore"

    # 1) 無ければ common を作成
    if not gitignore_path.exists():
        common = _render_template(
            "gitignore_common.j2",
            contest=contest,
        )
        gitignore_path.write_text(
            common.rstrip("\n") + "\n",
            encoding="utf-8",
        )
        print("🧹 .gitignore created (common)")

    # 2) 指定された言語だけ追記
    for lang in languages:
        tmpl_name = f"gitignore_{lang}.j2"
        marker = f"gitignore:{lang}"

        try:
            block = _render_template(
                tmpl_name,
                contest=contest,
            )
        except Exception:
            print(f"⚠️ no gitignore template for language: {lang}")
            continue

        if _append_block_if_missing(gitignore_path, marker, block):
            print(f"🧹 .gitignore appended ({lang})")


def generate_java(contest: str):
    print("\n☕ Generating Java skeleton & JUnit tests")
    subprocess.check_call(
        ["python3", "setup-java.py", contest, ",".join(PROBLEMS)]
    )
    print("✅ Java generation finished")


def generate_python(contest: str):
    print("\n🐍 Generating Python skeleton")
    subprocess.check_call(
        ["python3", "setup-python.py", contest, ",".join(PROBLEMS)]
    )
    print("✅ Python generation finished")


def load_default_languages_txt() -> list[str] | None:
    """
    default_lang.txt を読む。
    - 1 行 1 言語
    - 空行・'#' で始まる行は無視
    例:
        # default languages
        java
        python
    """
    p = Path(__file__).resolve().parent / "default_lang.txt"
    if not p.exists():
        return None

    languages: list[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue          # 空行を無視
        if line.startswith("#"):
            continue          # コメント行を無視
        languages.append(line)

    return languages or None


def main():
    parser = argparse.ArgumentParser(
        description="AtCoder contest setup tool"
    )
    parser.add_argument(
        "contest",
        nargs="?",
        help="contest id (e.g. abc421)"
    )
    parser.add_argument(
        "--java",
        action="store_true",
        help="generate Java code"
    )
    parser.add_argument(
        "--python",
        action="store_true",
        help="generate Python code (future)"
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="download https://atcoder.jp/ HTML as web.html and exit"
    )

    args = parser.parse_args()

    # --login が指定された場合は他のオプションを無視して終了
    if args.login:
        url = "https://atcoder.jp/"
        cookies = load_cookies()

        print(f"🌐 fetching: {url}")
        html = download_html(url, cookies=cookies, wait=0)

        # userScreenName を抽出
        m = re.search(
            r'var\s+userScreenName\s*=\s*"([^"]*)"\s*;',
            html
        )
        user = m.group(1) if m else ""

        if user:
            print(f"👤 Screen Name: {user}")
        else:
            print("⚠️  Not logged in (login required)")

        return

    # 通常モードでは contest 必須
    if not args.contest:
        parser.error("contest is required unless --login is specified")
    contest = args.contest.lower()

    # 生成する言語を決定
    # 1) CLI オプションが最優先
    languages: list[str] = []
    if args.java:
        languages.append("java")
    if args.python:
        languages.append("python")
    print(f"🏁 Contest: {contest.upper()}")

    # ① scrape
    scrape_contest(contest)

    # ② generate codes
    if not languages:
        # 2) default_lang.txt
        cfg = load_default_languages_txt()
        if cfg:
            languages = [x for x in cfg if x in SUPPORTED_LANGUAGES]

    if not languages:
        # 3) フォールバック：すべて
        languages = SUPPORTED_LANGUAGES.copy()

    generated_languages = []
    for lang in languages:
        if lang == "java":
            generate_java(contest)
            generated_languages.append("java")
        elif lang == "python":
            generate_python(contest)
            generated_languages.append("python")

    # ③ .gitignore
    ensure_gitignore_split(contest, generated_languages)

    print("\n🎉 setup.py completed successfully")


if __name__ == "__main__":
    main()
