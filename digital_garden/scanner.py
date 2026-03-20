"""目录扫描器 — 分析目录结构并报告混乱程度"""

from collections import Counter
from pathlib import Path

from colorama import Fore, Style
from tabulate import tabulate

from .utils import FileInfo, collect_files, days_since_access


class DirectoryScanner:
    """扫描目录并生成混乱度报告"""

    STALE_THRESHOLD_DAYS = 180

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.files: list[FileInfo] = []
        self._scanned = False

    def scan(self) -> list[FileInfo]:
        print(f"\n{Fore.CYAN}正在扫描目录: {self.target_dir}{Style.RESET_ALL}")
        self.files = collect_files(self.target_dir)
        self._scanned = True
        print(f"  找到 {Fore.YELLOW}{len(self.files)}{Style.RESET_ALL} 个文件")
        return self.files

    def report(self) -> dict:
        """生成完整的混乱度报告"""
        if not self._scanned:
            self.scan()

        if not self.files:
            print(f"\n{Fore.GREEN}目录为空，无需整理。{Style.RESET_ALL}")
            return {"total": 0}

        stats = self._compute_stats()
        self._print_report(stats)
        return stats

    def _compute_stats(self) -> dict:
        total_size = sum(f.size for f in self.files)
        category_counter = Counter(f.category for f in self.files)
        suffix_counter = Counter(f.suffix for f in self.files)

        size_groups = self._group_by_size()
        potential_duplicates = sum(
            len(paths) for paths in size_groups.values() if len(paths) > 1
        )

        stale_files = [
            f for f in self.files
            if days_since_access(f.path) > self.STALE_THRESHOLD_DAYS
        ]

        depth_counts = Counter(
            len(f.path.relative_to(self.target_dir).parts) for f in self.files
        )

        chaos_score = self._calculate_chaos_score(
            len(self.files), potential_duplicates, len(stale_files),
            len(category_counter), max(depth_counts.keys(), default=0)
        )

        return {
            "total": len(self.files),
            "total_size": total_size,
            "total_size_human": self._human_size(total_size),
            "categories": dict(category_counter.most_common()),
            "top_extensions": dict(suffix_counter.most_common(10)),
            "potential_duplicates": potential_duplicates,
            "stale_files": len(stale_files),
            "stale_file_list": stale_files[:20],
            "max_depth": max(depth_counts.keys(), default=0),
            "chaos_score": chaos_score,
        }

    def _group_by_size(self) -> dict[int, list[FileInfo]]:
        """按文件大小分组（快速预筛选疑似重复文件）"""
        groups: dict[int, list[FileInfo]] = {}
        for f in self.files:
            if f.size == 0:
                continue
            groups.setdefault(f.size, []).append(f)
        return groups

    @staticmethod
    def _calculate_chaos_score(
        total: int, duplicates: int, stale: int,
        categories: int, max_depth: int
    ) -> int:
        """计算混乱度分数 (0-100)，越高越乱"""
        score = 0
        if total > 0:
            dup_ratio = duplicates / total
            score += min(dup_ratio * 40, 40)
            stale_ratio = stale / total
            score += min(stale_ratio * 30, 30)
        if max_depth > 5:
            score += min((max_depth - 5) * 5, 15)
        if categories > 5:
            score += min((categories - 5) * 3, 15)
        return min(int(score), 100)

    def _print_report(self, stats: dict):
        chaos = stats["chaos_score"]
        if chaos < 20:
            chaos_label = f"{Fore.GREEN}整洁 ✓{Style.RESET_ALL}"
        elif chaos < 50:
            chaos_label = f"{Fore.YELLOW}轻度混乱{Style.RESET_ALL}"
        elif chaos < 80:
            chaos_label = f"{Fore.RED}中度混乱{Style.RESET_ALL}"
        else:
            chaos_label = f"{Fore.RED}{Style.BRIGHT}严重混乱 ✗{Style.RESET_ALL}"

        print(f"\n{'='*60}")
        print(f"  {Fore.CYAN}{Style.BRIGHT}目录健康报告{Style.RESET_ALL}")
        print(f"{'='*60}")
        print(f"  目录路径:    {self.target_dir}")
        print(f"  文件总数:    {stats['total']}")
        print(f"  总大小:      {stats['total_size_human']}")
        print(f"  最大深度:    {stats['max_depth']} 层")
        print(f"  混乱度评分:  {chaos}/100 — {chaos_label}")

        print(f"\n  {Fore.CYAN}文件类型分布:{Style.RESET_ALL}")
        cat_table = [[cat, count] for cat, count in stats["categories"].items()]
        print(tabulate(cat_table, headers=["类型", "数量"], tablefmt="simple",
                       colalign=("left", "right")))

        print(f"\n  {Fore.CYAN}热门后缀 (Top 10):{Style.RESET_ALL}")
        ext_table = [[ext or "(无后缀)", count]
                     for ext, count in stats["top_extensions"].items()]
        print(tabulate(ext_table, headers=["后缀", "数量"], tablefmt="simple",
                       colalign=("left", "right")))

        if stats["potential_duplicates"] > 0:
            print(f"\n  {Fore.YELLOW}[!] 疑似重复文件: "
                  f"{stats['potential_duplicates']} 个{Style.RESET_ALL}")
            print(f"    (基于文件大小预筛选，运行 deduplicate 进行精确校验)")

        if stats["stale_files"] > 0:
            print(f"\n  {Fore.YELLOW}[!] 超过 {self.STALE_THRESHOLD_DAYS} 天未访问的文件: "
                  f"{stats['stale_files']} 个{Style.RESET_ALL}")
            for sf in stats["stale_file_list"][:5]:
                rel = sf.path.relative_to(self.target_dir)
                age = days_since_access(sf.path)
                print(f"    - {rel}  ({age} 天前)")
            if stats["stale_files"] > 5:
                print(f"    ... 还有 {stats['stale_files'] - 5} 个")

        print(f"\n{'='*60}\n")

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
