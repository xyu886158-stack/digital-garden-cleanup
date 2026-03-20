"""deduplicator 模块单元测试"""

import tempfile
from pathlib import Path

import pytest

from digital_garden.deduplicator import Deduplicator


@pytest.fixture
def dup_dir():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        content_a = "identical content here\n" * 50
        (root / "file_a.txt").write_text(content_a, encoding="utf-8")
        (root / "file_a_copy.txt").write_text(content_a, encoding="utf-8")
        sub = root / "nested"
        sub.mkdir()
        (sub / "file_a_backup.txt").write_text(content_a, encoding="utf-8")

        (root / "unique.txt").write_text("this is unique", encoding="utf-8")
        (root / "unique2.py").write_text("print('unique')", encoding="utf-8")
        yield root


@pytest.fixture
def no_dup_dir():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "a.txt").write_text("aaa", encoding="utf-8")
        (root / "b.txt").write_text("bbb", encoding="utf-8")
        (root / "c.txt").write_text("ccc", encoding="utf-8")
        yield root


class TestDeduplicator:
    def test_find_duplicates(self, dup_dir):
        dedup = Deduplicator(dup_dir)
        groups = dedup.find_duplicates()
        assert len(groups) == 1
        group = list(groups.values())[0]
        assert len(group) == 3

    def test_no_duplicates(self, no_dup_dir):
        dedup = Deduplicator(no_dup_dir)
        groups = dedup.find_duplicates()
        assert len(groups) == 0

    def test_execute_moves_files(self, dup_dir):
        backup = dup_dir / "_test_backup"
        dedup = Deduplicator(dup_dir, backup_dir=backup)
        dedup.find_duplicates()
        moved = dedup.execute(auto_confirm=True)
        assert moved == 2

        remaining_txt = list(dup_dir.rglob("*.txt"))
        remaining_txt = [f for f in remaining_txt
                         if "_test_backup" not in str(f)]
        assert len(remaining_txt) == 2  # 1 kept + 1 unique

    def test_backup_dir_created(self, dup_dir):
        backup = dup_dir / "_test_backup"
        dedup = Deduplicator(dup_dir, backup_dir=backup)
        dedup.find_duplicates()
        dedup.execute(auto_confirm=True)
        assert backup.exists()
        backup_files = list(backup.rglob("*"))
        file_count = sum(1 for f in backup_files if f.is_file())
        assert file_count == 2

    def test_log_generated(self, dup_dir):
        dedup = Deduplicator(dup_dir)
        dedup.find_duplicates()
        dedup.execute(auto_confirm=True)
        logs = list(dup_dir.glob("organized_log_*.md"))
        assert len(logs) >= 1
