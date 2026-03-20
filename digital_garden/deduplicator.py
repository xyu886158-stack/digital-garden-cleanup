"""重复文件识别与安全处理"""

import shutil
from collections import defaultdict
from pathlib import Path

from colorama import Fore, Style
from tabulate import tabulate

from .logger import OperationLogger
from .utils import FileInfo, collect_files, compute_hash, ensure_dir


class Deduplicator:
    """基于 SHA-256 哈希精确识别重复文件"""

    def __init__(self, target_dir: Path, backup_dir: Path | None = None):
        self.target_dir = target_dir
        self.backup_dir = backup_dir or (target_dir / "_backup" / "duplicates")
        self.files: list[FileInfo] = []
        self.duplicate_groups: dict[str, list[FileInfo]] = {}

    def find_duplicates(self) -> dict[str, list[FileInfo]]:
        """两阶段重复检测: 大小预筛选 → 哈希精确匹配"""
        print(f"\n{Fore.CYAN}正在扫描文件...{Style.RESET_ALL}")
        self.files = collect_files(self.target_dir)
        non_empty = [f for f in self.files if f.size > 0]
        print(f"  找到 {len(non_empty)} 个非空文件")

        # 阶段 1: 按大小分组
        print(f"{Fore.CYAN}阶段 1: 按文件大小预筛选...{Style.RESET_ALL}")
        size_groups: dict[int, list[FileInfo]] = defaultdict(list)
        for f in non_empty:
            size_groups[f.size].append(f)

        candidates = {
            size: files for size, files in size_groups.items()
            if len(files) > 1
        }

        candidate_count = sum(len(v) for v in candidates.values())
        if candidate_count == 0:
            print(f"  {Fore.GREEN}未发现疑似重复文件。{Style.RESET_ALL}\n")
            return {}

        print(f"  发现 {candidate_count} 个文件大小相同，需要进一步校验")

        # 阶段 2: SHA-256 精确匹配
        print(f"{Fore.CYAN}阶段 2: 计算 SHA-256 哈希...{Style.RESET_ALL}")
        hash_groups: dict[str, list[FileInfo]] = defaultdict(list)
        checked = 0
        for size, files in candidates.items():
            for f in files:
                try:
                    file_hash = compute_hash(f.path)
                    hash_groups[file_hash].append(f)
                    checked += 1
                except (PermissionError, OSError) as e:
                    print(f"  {Fore.RED}跳过: {f.path} ({e}){Style.RESET_ALL}")

        self.duplicate_groups = {
            h: files for h, files in hash_groups.items()
            if len(files) > 1
        }

        total_dups = sum(len(v) - 1 for v in self.duplicate_groups.values())
        print(f"  校验了 {checked} 个文件，"
              f"发现 {Fore.YELLOW}{len(self.duplicate_groups)}{Style.RESET_ALL} 组重复 "
              f"(共 {Fore.YELLOW}{total_dups}{Style.RESET_ALL} 个冗余文件)\n")

        return self.duplicate_groups

    def show_duplicates(self):
        """展示重复文件详情"""
        if not self.duplicate_groups:
            print(f"{Fore.GREEN}没有重复文件。{Style.RESET_ALL}")
            return

        for i, (h, files) in enumerate(self.duplicate_groups.items(), 1):
            print(f"{Fore.CYAN}重复组 #{i}{Style.RESET_ALL} "
                  f"(哈希: {h[:12]}... | 大小: {files[0].size_human})")
            rows = []
            for j, f in enumerate(files):
                rel = f.path.relative_to(self.target_dir)
                keep = f"{Fore.GREEN}保留{Style.RESET_ALL}" if j == 0 else f"{Fore.RED}移除{Style.RESET_ALL}"
                rows.append([keep, str(rel), f.modified_time.strftime("%Y-%m-%d %H:%M")])
            print(tabulate(rows, headers=["操作", "路径", "修改时间"],
                           tablefmt="simple"))
            print()

    def execute(self, auto_confirm: bool = False) -> int:
        """执行去重：保留每组第一个，其余移至备份目录"""
        if not self.duplicate_groups:
            print(f"{Fore.GREEN}没有需要处理的重复文件。{Style.RESET_ALL}")
            return 0

        self.show_duplicates()

        total_to_move = sum(len(v) - 1 for v in self.duplicate_groups.values())
        total_save_size = sum(
            f.size for files in self.duplicate_groups.values()
            for f in files[1:]
        )

        print(f"{Fore.YELLOW}即将移动 {total_to_move} 个冗余文件到备份目录:{Style.RESET_ALL}")
        print(f"  {self.backup_dir}")
        print(f"  预计释放空间: {self._human_size(total_save_size)}")

        if not auto_confirm:
            answer = input(f"\n{Fore.YELLOW}确认执行? (y/N): {Style.RESET_ALL}").strip().lower()
            if answer != "y":
                print(f"{Fore.RED}操作已取消。{Style.RESET_ALL}")
                return 0

        ensure_dir(self.backup_dir)
        logger = OperationLogger(self.target_dir)
        logger.start("重复文件清理")
        logger.log_section("移动记录")

        moved = 0
        for h, files in self.duplicate_groups.items():
            for f in files[1:]:
                try:
                    rel = f.path.relative_to(self.target_dir)
                    dest = self.backup_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)

                    if dest.exists():
                        stem = dest.stem
                        suffix = dest.suffix
                        counter = 1
                        while dest.exists():
                            dest = dest.with_name(f"{stem}_{counter}{suffix}")
                            counter += 1

                    shutil.move(str(f.path), str(dest))
                    logger.log_move(f.path, dest, f"重复 (哈希: {h[:12]}...)")
                    moved += 1
                except (PermissionError, OSError) as e:
                    print(f"  {Fore.RED}移动失败: {f.path} ({e}){Style.RESET_ALL}")

        logger.log_summary(len(self.files), moved, self._human_size(total_save_size))
        log_path = logger.save()

        print(f"\n{Fore.GREEN}完成! 移动了 {moved} 个冗余文件。{Style.RESET_ALL}")
        print(f"日志已保存: {log_path}")
        return moved

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
