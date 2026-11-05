#!/usr/bin/env python3
"""Regenerate the local-file-safe course manifest (Python standard library only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "courses.json"
TARGET = ROOT / "courses-data.js"
HEADER = "/* Generated from courses.json; run python3 scripts/build_course_data.py. */\n"


def render() -> str:
    manifest = json.loads(SOURCE.read_text(encoding="utf-8"))
    courses = manifest.get("chapters")
    if not isinstance(courses, list) or not courses:
        raise ValueError("chapters must be a non-empty list")
    if manifest.get("chapterCount") != len(courses):
        raise ValueError("chapterCount must equal the number of chapters")
    seen = set()
    for item in courses:
        if not isinstance(item, dict):
            raise ValueError("chapter entry is not an object")
        number, filename = item.get("num"), item.get("file")
        if not isinstance(number, str) or not isinstance(filename, str):
            raise ValueError("chapter num and file must be strings")
        if not re.fullmatch(r"[0-9]{2}\.html", filename) or filename != number + ".html":
            raise ValueError("unsafe or mismatched chapter filename")
        if filename in seen:
            raise ValueError("duplicate chapter file")
        if not (ROOT / filename).is_file():
            raise ValueError("missing chapter HTML: " + filename)
        seen.add(filename)
    return HEADER + "window.LLAMA_COURSES = " + json.dumps(
        manifest, ensure_ascii=False, indent=2
    ) + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated manifest is stale")
    args = parser.parse_args()
    try:
        expected = render()
        if args.check:
            if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != expected:
                print("courses-data.js is out of date; regenerate it", file=sys.stderr)
                return 1
            print("courses-data.js is synchronized with courses.json")
        else:
            TARGET.write_text(expected, encoding="utf-8")
            print("regenerated courses-data.js")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("course data validation failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
