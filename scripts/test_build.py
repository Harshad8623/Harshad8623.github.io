"""Dependency-free regression tests for the GitHub Pages static build.

Run: python scripts/test_build.py
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]


def make_fixture(path: Path) -> None:
    """Create a small site whose content tests can safely change."""
    for rel in ("content/site.json", "index.html", "assets/site.js"):
        dst = path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SRC / rel, dst)
    (path / "assets/uploads/images").mkdir(parents=True)
    (path / "assets/uploads/documents").mkdir(parents=True)
    (path / "assets/uploads/documents/example-resume.pdf").write_bytes(b"%PDF-1.4\n% TEST ONLY")
    (path / "assets/uploads/images/नमुना-प्रमाणपत्र.png").write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"TEST ONLY"
    )
    for collection in ("projects", "resumes", "certificates"):
        (path / "content" / collection).mkdir(parents=True)
    (path / "scripts").mkdir()
    shutil.copy(SRC / "scripts/build.py", path / "scripts/build.py")


def build(path: Path) -> dict:
    subprocess.run([sys.executable, str(path / "scripts/build.py")], cwd=path, check=True, capture_output=True, text=True)
    return json.loads((path / "dist/site-data.json").read_text(encoding="utf-8"))


class PortfolioBuildTests(unittest.TestCase):
    def test_published_hidden_and_unicode_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            items = [
                ("projects/public.json", {"id": "public", "name": "Python project", "published": True, "order": 1, "image": ""}),
                ("projects/private.json", {"id": "private", "name": "Hidden", "published": False, "order": 0}),
                ("resumes/public.json", {"label": "Python resume", "role": "Backend", "file": "/assets/uploads/documents/example-resume.pdf", "published": True}),
                ("resumes/private.json", {"label": "Hidden CV", "file": "/assets/uploads/documents/example-resume.pdf", "published": False}),
                ("certificates/public.json", {"title": "मराठी प्रमाणपत्र", "issuer": "Sample issuer", "image": "/assets/uploads/images/नमुना-प्रमाणपत्र.png", "published": True}),
                ("certificates/private.json", {"title": "Hidden certificate", "published": False}),
            ]
            for rel, data in items:
                (root / "content" / rel).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            result = build(root)
            self.assertEqual([p["id"] for p in result["site"]["projects"]], ["public"])
            self.assertEqual(len(result["resumes"]), 1)
            self.assertEqual(result["resumes"][0]["mime"], "PDF")
            self.assertEqual(result["resumes"][0]["file"], "assets/uploads/documents/example-resume.pdf")
            self.assertEqual(len(result["certificates"]), 1)
            self.assertEqual(result["certificates"][0]["title"], "मराठी प्रमाणपत्र")
            self.assertTrue((root / "dist/assets/uploads/images/नमुना-प्रमाणपत्र.png").exists())
            self.assertNotIn("Hidden certificate", (root / "dist/site-data.json").read_text(encoding="utf-8"))
            self.assertFalse((root / "dist/content/site.json").exists())
            self.assertFalse((root / "dist/scripts/build.py").exists())
            self.assertTrue((root / "dist/robots.txt").exists())
            self.assertTrue((root / "dist/sitemap.xml").exists())

    def test_rejects_unsafe_media_paths(self) -> None:
        spec = importlib.util.spec_from_file_location("portfolio_site_build_test", SRC / "scripts/build.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        for value in (
            "../../secret.env", "/assets/../../secret.env", "assets/../secret.env",
            "file:///etc/passwd", "javascript:alert(1)", "assets/this-does-not-exist.pdf",
            "assets/uploads/documents/example.pdf?token=123", "assets/\\malicious",
            "data:text/html,test",
        ):
            self.assertEqual(module.public_media(value), "", msg=value)
        self.assertEqual(module.public_media("https://example.com/demo.jpg"), "https://example.com/demo.jpg")

    def test_rejects_duplicate_and_invalid_project_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            for name in ("alpha.json", "beta.json"):
                (root / "content/projects" / name).write_text(
                    json.dumps({"id": "duplicate", "name": name}), encoding="utf-8"
                )
            result = subprocess.run([sys.executable, str(root / "scripts/build.py")], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Duplicate project ID", result.stderr)

    def test_real_seeded_content_and_navigation(self) -> None:
        # The shipped project has projects even before CMS adds resumes/certificates.
        projects = sorted((SRC / "content/projects").glob("*.json"))
        self.assertGreaterEqual(len(projects), 3)
        site = json.loads((SRC / "content/site.json").read_text(encoding="utf-8"))
        self.assertEqual(site["profile"]["marathiName"], "हर्षद माधव धुप्पे")
        self.assertEqual(site["profile"]["name"], "Harshad Madhav Dhuppe")
        for filename in (".pages.yml", ".github/workflows/pages.yml", "assets/v3.css", "assets/site.js"):
            self.assertTrue((SRC / filename).is_file(), filename)
        for filename in ("content/projects", "content/resumes", "content/certificates"):
            self.assertTrue((SRC / filename).is_dir(), filename)
        self.assertIn("id=\"project-search\"", (SRC / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
