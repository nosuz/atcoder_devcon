#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def load_cache(contest_dir: Path, problem: str) -> dict:
    path = contest_dir / "cache" / f"{problem}.json"
    if not path.exists():
        raise FileNotFoundError(f"cache not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_if_absent(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def strip_last_newline(s: str) -> str:
    # 入力例は通常末尾に \n が付いているので「最後の1個だけ」落とす
    return s[:-1] if s.endswith("\n") else s


def escape_java_string(s: str) -> str:
    # Java の "..." に安全に入るようにエスケープ
    return (
        s.replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\r", "\\r")
         .replace("\n", "\\n")
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("contest", help="e.g. abc438")
    ap.add_argument("problems", help="e.g. A,B,C")

    # 手動指定もできるように残しつつ、デフォルトは自動検出
    ap.add_argument(
        "--java-version",
        type=int,
        default=None,
        help="override Java major version for Gradle toolchain (e.g. 21). "
             "If omitted, auto-detected from `java -version`.",
    )

    args = ap.parse_args()

    contest = args.contest.lower()
    contest_dir = Path(args.contest.upper())  # 例: ABC438
    if not contest_dir.exists():
        raise FileNotFoundError(
            f"contest dir not found: {contest_dir} (run setup.py first)")

    # templates/ ディレクトリ（setup-java.py と同じ場所を基準）
    tools_dir = Path(__file__).resolve().parent
    tmpl_dir = tools_dir / "templates"

    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )

    t_main = env.get_template("template_main.java")
    t_test = env.get_template("template_test.java")
    t_build = env.get_template("build.gradle.j2")
    t_settings = env.get_template("settings.gradle.j2")
    t_props = env.get_template("gradle.properties.j2")

    # Gradle 設定
    # build.gradle.j2 は junit-jupiter:5.10.2 を固定で持っている前提 :contentReference[oaicite:2]{index=2}
    write_if_absent(
        contest_dir / "build.gradle",
        t_build.render(),
    )
    write_if_absent(
        contest_dir / "settings.gradle",
        t_settings.render(project_name=contest_dir.name),
    )
    write_if_absent(
        contest_dir / "gradle.properties",
        t_props.render(),
    )

    # Java 出力先
    main_dir = contest_dir / "src" / "main" / "java" / contest
    test_dir = contest_dir / "src" / "test" / "java" / contest
    main_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    # A〜F を生成
    for p in [q.upper() for q in args.problems.split(",")]:
        data = load_cache(contest_dir, p)

        # main
        content = {
            "contest": contest,          # package
            "Name": p,                # クラス名 A/B/...
            "title": data.get("title", ""),
            "url": data.get("url", ""),
        }

        main_code = t_main.render(content=content)
        write_if_absent(main_dir / f"{p}.java", main_code)

        # test（examples を index 付き配列にしてテンプレへ）
        examples = data.get("examples", [])
        ex2 = []
        for i, ex in enumerate(examples):
            inp = strip_last_newline(ex["input"])
            out = strip_last_newline(ex["output"])
            ex2.append({
                "index": i + 1,
                "input": escape_java_string(inp),
                "output": escape_java_string(out),
            })

        test_code = t_test.render(
            content=content, examples=ex2)
        write_if_absent(test_dir / f"{p}Test.java", test_code)

    print(f"✅ Generated Java skeleton + JUnit + Gradle in: {contest_dir}")


if __name__ == "__main__":
    main()
