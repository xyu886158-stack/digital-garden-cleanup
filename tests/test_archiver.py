"""archiver 模块单元测试"""

import tempfile
from pathlib import Path

import pytest

from digital_garden.archiver import Archiver


@pytest.fixture
def messy_dir():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "report.pdf").write_text("pdf content", encoding="utf-8")
        (root / "photo.jpg").write_text("jpg content", encoding="utf-8")
        (root / "song.mp3").write_text("mp3 content", encoding="utf-8")
        (root / "code.py").write_text("print('hello')", encoding="utf-8")
        (root / "archive.zip").write_text("zip content", encoding="utf-8")
        (root / "notes.txt").write_text("my notes", encoding="utf-8")
        yield root


class TestArchiverByType:
    def test_analyze_creates_plan(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="type")
        plan = archiver.analyze()
        assert len(plan) == 6

    def test_execute_moves_files(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="type")
        archiver.analyze()
        moved = archiver.execute(auto_confirm=True)
        assert moved == 6

        assert (messy_dir / "文档").is_dir()
        assert (messy_dir / "图片").is_dir()
        assert (messy_dir / "音频").is_dir()
        assert (messy_dir / "代码").is_dir()
        assert (messy_dir / "压缩包").is_dir()

    def test_log_generated(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="type")
        archiver.analyze()
        archiver.execute(auto_confirm=True)
        logs = list(messy_dir.glob("organized_log_*.md"))
        assert len(logs) >= 1


class TestArchiverByTime:
    def test_analyze_creates_plan(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="time")
        plan = archiver.analyze()
        assert len(plan) > 0

    def test_execute_creates_year_month_dirs(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="time")
        archiver.analyze()
        moved = archiver.execute(auto_confirm=True)
        assert moved > 0

        year_dirs = [d for d in messy_dir.iterdir()
                     if d.is_dir() and d.name.isdigit() and len(d.name) == 4]
        assert len(year_dirs) >= 1


class TestArchiverDryRun:
    def test_dry_run_does_not_move(self, messy_dir):
        archiver = Archiver(messy_dir, strategy="type")
        archiver.analyze()
        archiver.show_plan()
        assert (messy_dir / "report.pdf").exists()
        assert (messy_dir / "photo.jpg").exists()
