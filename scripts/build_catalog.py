#!/usr/bin/env python3
"""Build/check the file://-compatible browser catalog from canonical courses.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_FILE = re.compile(r"[0-9]{2}\.html\Z")
HEADER = "// Auto-generated from courses.json. Run: python scripts/build_catalog.py --write\n"


def build(root: Path) -> str:
    data = json.loads((root / "courses.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("courses.json must be an object")
    for key in ("title", "emoji", "subtitle"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"missing or invalid {key}")
    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("chapters must be a nonempty array")
    if type(data.get("chapterCount")) is not int or data["chapterCount"] != len(chapters):
        raise ValueError("chapterCount does not match chapters")
    seen_nums: set[str] = set()
    seen_files: set[str] = set()
    for pos, chapter in enumerate(chapters, 1):
        if not isinstance(chapter, dict):
            raise ValueError(f"chapter {pos} must be an object")
        num = chapter.get("num")
        file = chapter.get("file")
        title = chapter.get("title")
        topics = chapter.get("topics")
        if not isinstance(num, str) or num != f"{pos:02d}":
            raise ValueError(f"chapter {pos} has invalid or nonsequential number")
        if not isinstance(file, str) or not CHAPTER_FILE.fullmatch(file) or file != f"{num}.html":
            raise ValueError(f"chapter {num} has an unsafe or incorrect filename")
        if num in seen_nums or file in seen_files:
            raise ValueError(f"chapter {num} is duplicated")
        seen_nums.add(num)
        seen_files.add(file)
        if not (root / file).is_file() or (root / file).is_symlink():
            raise ValueError(f"chapter {num} points to a missing or unsafe HTML file")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"chapter {num} has an invalid title")
        if not isinstance(topics, list) or not all(isinstance(t, str) and t.strip() for t in topics):
            raise ValueError(f"chapter {num} has invalid topics")
    return HEADER + "window.LLAMA_COURSES = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="regenerate courses.js")
    group.add_argument("--check", action="store_true", help="verify courses.js is fresh")
    args = parser.parse_args(argv)
    try:
        expected = build(ROOT)
        output = ROOT / "courses.js"
        if args.write:
            output.write_text(expected, encoding="utf-8")
            print(f"Generated {output.name}")
            return 0
        if not output.exists() or output.read_text(encoding="utf-8") != expected:
            print("courses.js is stale: run python scripts/build_catalog.py --write", file=sys.stderr)
            return 1
        print("courses.js matches courses.json and chapter files")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Catalog validation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
