"""scanner 模块单元测试"""

import tempfile
from pathlib import Path

import pytest

from digital_garden.scanner import DirectoryScanner


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "doc1.txt").write_text("hello world", encoding="utf-8")
        (root / "doc2.txt").write_text("another file", encoding="utf-8")
        (root / "image.png").write_bytes(b"\x89PNG" + b"\x00" * 100)
        sub = root / "subdir"
        sub.mkdir()
        (sub / "code.py").write_text("print('hi')", encoding="utf-8")
        (sub / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        yield root


@pytest.fixture
def empty_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestDirectoryScanner:
    def test_scan_finds_all_files(self, temp_dir):
        scanner = DirectoryScanner(temp_dir)
        files = scanner.scan()
        assert len(files) == 5

    def test_report_returns_stats(self, temp_dir):
        scanner = DirectoryScanner(temp_dir)
        stats = scanner.report()
        assert stats["total"] == 5
        assert "categories" in stats
        assert "chaos_score" in stats

    def test_empty_directory(self, empty_dir):
        scanner = DirectoryScanner(empty_dir)
        stats = scanner.report()
        assert stats["total"] == 0

    def test_categories_present(self, temp_dir):
        scanner = DirectoryScanner(temp_dir)
        stats = scanner.report()
        assert "文档" in stats["categories"]
        assert "代码" in stats["categories"]

    def test_chaos_score_range(self, temp_dir):
        scanner = DirectoryScanner(temp_dir)
        stats = scanner.report()
        assert 0 <= stats["chaos_score"] <= 100
