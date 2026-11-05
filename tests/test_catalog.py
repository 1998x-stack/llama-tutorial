"""No-network regression tests for the LLaMA tutorial's offline catalog."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_catalog", ROOT / "scripts/build_catalog.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for i in (1, 2):
            (self.root / f"{i:02d}.html").write_text("<!doctype html><html></html>", encoding="utf-8")
        self.data = {
            "title": "LLaMA 教程", "emoji": "🦙", "subtitle": "离线课程", "chapterCount": 2,
            "chapters": [
                {"num": f"{i:02d}", "title": f"章节{i}", "topics": ["RoPE"], "file": f"{i:02d}.html"}
                for i in (1, 2)
            ],
        }
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        (self.root / "courses.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_build_deterministic_offline_catalog(self):
        first = module.build(self.root)
        self.assertEqual(first, module.build(self.root))
        self.assertTrue(first.startswith(module.HEADER))
        payload = first.split("window.LLAMA_COURSES = ", 1)[1].removesuffix(";\n")
        self.assertEqual(json.loads(payload), self.data)

    def test_chapter_count_mismatch_rejected(self):
        self.data["chapterCount"] = 3
        self.save()
        with self.assertRaisesRegex(ValueError, "chapterCount"):
            module.build(self.root)

    def test_missing_link_rejected(self):
        (self.root / "02.html").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            module.build(self.root)

    def test_path_traversal_rejected(self):
        self.data["chapters"][0]["file"] = "../01.html"
        self.save()
        with self.assertRaisesRegex(ValueError, "unsafe"):
            module.build(self.root)

    def test_duplicate_number_rejected(self):
        self.data["chapters"][1]["num"] = "01"
        self.save()
        with self.assertRaisesRegex(ValueError, "nonsequential"):
            module.build(self.root)

    def test_catalog_requires_valid_topics(self):
        self.data["chapters"][0]["topics"] = [""]
        self.save()
        with self.assertRaisesRegex(ValueError, "topics"):
            module.build(self.root)

    def test_real_course_catalog_and_links(self):
        data = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
        self.assertEqual(28, len(data["chapters"]))
        self.assertEqual(module.build(ROOT), (ROOT / "courses.js").read_text(encoding="utf-8"))

    def test_local_index_uses_browser_script_not_fetch(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<script src="courses.js"></script>', html)
        self.assertNotIn("fetch('courses.json')", html)
        self.assertIn("message.textContent = msg", html)
        self.assertIn("link.textContent = '开始学习 ' + course.num", html)


if __name__ == "__main__":
    unittest.main()
