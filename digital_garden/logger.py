"""操作日志生成器 — 每次操作生成 organized_log.md"""

from datetime import datetime
from pathlib import Path


class OperationLogger:
    """记录所有文件操作到 Markdown 日志文件"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = self.log_dir / f"organized_log_{timestamp}.md"
        self._entries: list[str] = []
        self._header_written = False

    def _write_header(self, operation: str):
        self._header_written = True
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._entries.append(f"# 文件整理日志\n")
        self._entries.append(f"- **操作类型**: {operation}")
        self._entries.append(f"- **执行时间**: {now}")
        self._entries.append(f"")

    def log_move(self, source: Path, destination: Path, reason: str = ""):
        self._entries.append(
            f"| `{source}` | `{destination}` | {reason} |"
        )

    def log_section(self, title: str):
        self._entries.append(f"\n## {title}\n")
        self._entries.append("| 原路径 | 目标路径 | 原因 |")
        self._entries.append("|--------|----------|------|")

    def log_summary(self, total_files: int, moved_files: int, saved_space: str = ""):
        self._entries.append(f"\n## 统计摘要\n")
        self._entries.append(f"- **扫描文件数**: {total_files}")
        self._entries.append(f"- **移动文件数**: {moved_files}")
        if saved_space:
            self._entries.append(f"- **释放空间**: {saved_space}")

    def log_info(self, message: str):
        self._entries.append(f"\n> {message}\n")

    def start(self, operation: str):
        self._write_header(operation)

    def save(self) -> Path:
        """将日志写入文件并返回路径"""
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self._entries))
        return self.log_path
