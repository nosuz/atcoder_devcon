#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
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
    return s[:-1] if s.endswith("\n") else s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("contest", help="e.g. abc421")
    ap.add_argument("problems", help="e.g. A,B,C")
    args = ap.parse_args()

    contest = args.contest.lower()
    contest_dir = Path(args.contest.upper())  # 例: ABC421
    if not contest_dir.exists():
        raise FileNotFoundError(
            f"contest dir not found: {contest_dir} (run setup.py first)"
        )

    # templates/ ディレクトリ（setup-python.py と同じ場所を基準）
    tools_dir = Path(__file__).resolve().parent
    tmpl_dir = tools_dir / "templates"

    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )

    # 添付の template_main.py を使う :contentReference[oaicite:2]{index=2}
    t_main = env.get_template("template_main.py")
    t_test = env.get_template("template_test.py")

    # 出力先：
    #  - 提出しやすいようにコンテスト直下に A.py〜F.py を作る
    out_dir = contest_dir
    tests_dir = contest_dir / "tests"

    # pytest 設定（無くても動くが、検出が安定する）
    write_if_absent(
        contest_dir / "pytest.ini",
        "[pytest]\npython_files = test_*.py\naddopts = -q\n",
    )

    for p in [q.upper() for q in args.problems.split(",")]:
        data = load_cache(contest_dir, p)

        # template_main.py は {{contents.title}} / {{contents.url}} を参照している :contentReference[oaicite:3]{index=3}
        contents = {
            "title": data.get("title", ""),
            "url": data.get("url", ""),
            "contest": contest,
            "problem": p,
        }

        raw_examples = data.get("examples", [])
        examples = []
        for ex in raw_examples:
            examples.append({
                "index": len(examples) + 1,
                "input": strip_last_newline(ex.get("input", "")),
                "output": strip_last_newline(ex.get("output", "")),
            })

        code = t_main.render(contents=contents, examples=examples)

        write_if_absent(out_dir / f"{p}.py", code)

        # pytest テスト生成
        test_code = t_test.render(contents=contents, examples=examples)
        write_if_absent(tests_dir / f"test_{p.lower()}.py", test_code)

    print(f"✅ Generated Python skeleton + pytest tests in: {contest_dir}")
    print("   Run: cd {0} && pytest".format(contest_dir))


if __name__ == "__main__":
    main()
