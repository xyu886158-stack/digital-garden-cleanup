"""工具函数：哈希计算、文件元数据提取、文件类型映射"""

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CHUNK_SIZE = 8192

TYPE_MAP = {
    "文档": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
             ".txt", ".md", ".csv", ".rtf", ".odt", ".ods", ".odp", ".epub"},
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
             ".ico", ".tiff", ".tif", ".raw", ".psd", ".ai"},
    "视频": {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
             ".m4v", ".mpg", ".mpeg", ".3gp"},
    "音频": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
             ".opus", ".mid", ".midi"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
               ".tgz", ".iso", ".dmg"},
    "代码": {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
             ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift",
             ".kt", ".scala", ".html", ".css", ".scss", ".less", ".sql",
             ".sh", ".bat", ".ps1", ".json", ".xml", ".yaml", ".yml",
             ".toml", ".ini", ".cfg", ".conf"},
}

_EXT_TO_CATEGORY: dict[str, str] = {}
for category, extensions in TYPE_MAP.items():
    for ext in extensions:
        _EXT_TO_CATEGORY[ext] = category


@dataclass
class FileInfo:
    """文件元数据"""
    path: Path
    name: str
    suffix: str
    size: int
    created_time: datetime
    modified_time: datetime
    category: str

    @property
    def size_human(self) -> str:
        """人类可读的文件大小"""
        size = self.size
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


def compute_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """计算文件哈希值，支持 md5 和 sha256"""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def get_file_info(filepath: Path) -> FileInfo:
    """提取文件的完整元数据"""
    stat = filepath.stat()
    suffix = filepath.suffix.lower()
    category = _EXT_TO_CATEGORY.get(suffix, "其他")

    created_ts = stat.st_ctime
    modified_ts = stat.st_mtime

    return FileInfo(
        path=filepath,
        name=filepath.name,
        suffix=suffix,
        size=stat.st_size,
        created_time=datetime.fromtimestamp(created_ts),
        modified_time=datetime.fromtimestamp(modified_ts),
        category=category,
    )


def get_category(suffix: str) -> str:
    """根据后缀名返回文件分类"""
    return _EXT_TO_CATEGORY.get(suffix.lower(), "其他")


def collect_files(directory: Path, recursive: bool = True) -> list[FileInfo]:
    """收集目录下所有文件的元数据"""
    files: list[FileInfo] = []
    if recursive:
        iterator = directory.rglob("*")
    else:
        iterator = directory.glob("*")

    for p in iterator:
        if p.is_file() and not p.name.startswith("."):
            try:
                files.append(get_file_info(p))
            except (PermissionError, OSError):
                continue
    return files


def ensure_dir(path: Path) -> Path:
    """确保目录存在，不存在则创建"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def days_since_access(filepath: Path) -> int:
    """返回文件上次访问距今的天数"""
    atime = datetime.fromtimestamp(filepath.stat().st_atime)
    return (datetime.now() - atime).days
