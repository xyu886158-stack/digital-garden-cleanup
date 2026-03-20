"""生成测试数据到指定目录，模拟混乱的文件环境"""

import os
import random
import shutil
from pathlib import Path

TEST_DIR = Path(r"D:\Program\claude\test")


def clean_test_dir():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True, exist_ok=True)


def create_file(path: Path, content: str | bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def generate():
    clean_test_dir()
    print(f"正在生成测试数据到: {TEST_DIR}\n")

    # 1. 重复文件 — 相同内容不同名称/位置
    dup_content_1 = "这是一份重要的会议纪要，讨论了Q3的销售策略。\n" * 20
    create_file(TEST_DIR / "会议纪要_Q3.txt", dup_content_1)
    create_file(TEST_DIR / "docs" / "会议纪要_Q3_副本.txt", dup_content_1)
    create_file(TEST_DIR / "backup" / "old" / "会议纪要_Q3_备份.txt", dup_content_1)

    dup_content_2 = b"\x89PNG\r\n" + b"\x00" * 500 + b"fake_image_data_here" * 50
    create_file(TEST_DIR / "photo.png", dup_content_2)
    create_file(TEST_DIR / "images" / "photo_copy.png", dup_content_2)

    dup_content_3 = "def hello():\n    print('Hello World!')\n" * 30
    create_file(TEST_DIR / "script.py", dup_content_3)
    create_file(TEST_DIR / "projects" / "old_script.py", dup_content_3)

    # 2. 各种类型文件 — 散落在根目录
    create_file(TEST_DIR / "报告2024.pdf", "fake pdf content " * 100)
    create_file(TEST_DIR / "预算表.xlsx", "fake excel data " * 80)
    create_file(TEST_DIR / "演示文稿.pptx", "fake pptx slides " * 60)
    create_file(TEST_DIR / "README.md", "# My Project\n\nThis is a readme file.\n")
    create_file(TEST_DIR / "config.json", '{"key": "value", "debug": true}\n')
    create_file(TEST_DIR / "notes.txt", "随手记录的一些想法和灵感...\n" * 10)
    create_file(TEST_DIR / "todo.csv", "任务,状态,截止日期\n完成报告,进行中,2024-06-30\n" * 5)

    # 3. 图片文件
    for name in ["vacation_01.jpg", "vacation_02.jpg", "screenshot_2024.png", "avatar.webp"]:
        create_file(TEST_DIR / name, f"fake image data for {name} " * 50)

    # 4. 音视频文件
    create_file(TEST_DIR / "recording.mp3", "fake mp3 audio data " * 200)
    create_file(TEST_DIR / "lecture.mp4", "fake mp4 video data " * 500)
    create_file(TEST_DIR / "podcast.wav", "fake wav data " * 300)

    # 5. 压缩包
    create_file(TEST_DIR / "archive_2023.zip", "fake zip content " * 100)
    create_file(TEST_DIR / "backup.tar.gz", "fake tar.gz content " * 100)

    # 6. 嵌套目录里的文件
    create_file(TEST_DIR / "work" / "project_a" / "main.py", "print('project a')\n")
    create_file(TEST_DIR / "work" / "project_a" / "utils.py", "def helper(): pass\n")
    create_file(TEST_DIR / "work" / "project_b" / "index.html", "<html><body>Hello</body></html>\n")
    create_file(TEST_DIR / "personal" / "diary_2024.txt", "今天天气不错...\n" * 20)
    create_file(TEST_DIR / "personal" / "travel_plan.md", "# 旅行计划\n\n- 东京\n- 巴黎\n")

    # 7. 深层嵌套（模拟混乱）
    deep = TEST_DIR / "level1" / "level2" / "level3" / "level4" / "level5"
    create_file(deep / "buried_file.txt", "这个文件埋得很深，应该被整理出来。\n")
    create_file(deep / "data.csv", "col1,col2\n1,2\n3,4\n")

    # 8. 无后缀文件
    create_file(TEST_DIR / "Makefile", "all:\n\techo hello\n")
    create_file(TEST_DIR / "LICENSE", "MIT License\n\nCopyright 2024...\n")

    # 统计
    all_files = list(TEST_DIR.rglob("*"))
    file_count = sum(1 for f in all_files if f.is_file())
    dir_count = sum(1 for f in all_files if f.is_dir())
    print(f"生成完毕!")
    print(f"  文件数: {file_count}")
    print(f"  目录数: {dir_count}")
    print(f"  包含: 3组重复文件, 多种文件类型, 深层嵌套目录")


if __name__ == "__main__":
    generate()
