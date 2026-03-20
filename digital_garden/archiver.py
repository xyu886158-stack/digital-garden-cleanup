"""智能归档引擎 — 按时间或文件类型进行归档"""

import shutil
from pathlib import Path

from colorama import Fore, Style
from tabulate import tabulate

from .logger import OperationLogger
from .utils import FileInfo, collect_files, ensure_dir, get_category


class Archiver:
    """根据预设策略归档文件"""

    STRATEGY_TIME = "time"
    STRATEGY_TYPE = "type"

    def __init__(self, target_dir: Path, output_dir: Path | None = None,
                 strategy: str = "time"):
        self.target_dir = target_dir
        self.output_dir = output_dir or target_dir
        self.strategy = strategy
        self.files: list[FileInfo] = []
        self.plan: list[tuple[FileInfo, Path]] = []

    def analyze(self) -> list[tuple[FileInfo, Path]]:
        """分析并生成归档方案（不执行）"""
        print(f"\n{Fore.CYAN}正在分析目录: {self.target_dir}{Style.RESET_ALL}")
        print(f"  归档策略: {self._strategy_label()}")

        self.files = collect_files(self.target_dir)
        self.plan = []

        for f in self.files:
            dest = self._compute_destination(f)
            if dest and dest != f.path.parent:
                self.plan.append((f, dest))

        print(f"  需要归档的文件: {Fore.YELLOW}{len(self.plan)}{Style.RESET_ALL} / {len(self.files)}")
        return self.plan

    def show_plan(self):
        """展示归档方案"""
        if not self.plan:
            print(f"\n{Fore.GREEN}所有文件已在正确位置，无需归档。{Style.RESET_ALL}")
            return

        rows = []
        for f, dest in self.plan[:30]:
            src_rel = f.path.relative_to(self.target_dir)
            dest_rel = dest.relative_to(self.output_dir)
            rows.append([str(src_rel), str(dest_rel / f.name)])

        print(f"\n{Fore.CYAN}归档方案预览:{Style.RESET_ALL}")
        print(tabulate(rows, headers=["当前位置", "目标位置"], tablefmt="simple"))

        if len(self.plan) > 30:
            print(f"\n  ... 还有 {len(self.plan) - 30} 个文件")

    def execute(self, auto_confirm: bool = False) -> int:
        """执行归档方案"""
        if not self.plan:
            self.analyze()

        if not self.plan:
            print(f"{Fore.GREEN}无需归档。{Style.RESET_ALL}")
            return 0

        self.show_plan()

        print(f"\n{Fore.YELLOW}即将移动 {len(self.plan)} 个文件。{Style.RESET_ALL}")

        if not auto_confirm:
            answer = input(f"{Fore.YELLOW}确认执行? (y/N): {Style.RESET_ALL}").strip().lower()
            if answer != "y":
                print(f"{Fore.RED}操作已取消。{Style.RESET_ALL}")
                return 0

        logger = OperationLogger(self.target_dir)
        logger.start(f"文件归档 ({self._strategy_label()})")
        logger.log_section("移动记录")

        moved = 0
        for f, dest_dir in self.plan:
            try:
                ensure_dir(dest_dir)
                dest_path = dest_dir / f.name

                if dest_path.exists():
                    stem = dest_path.stem
                    suffix = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_path.with_name(f"{stem}_{counter}{suffix}")
                        counter += 1

                shutil.move(str(f.path), str(dest_path))
                logger.log_move(f.path, dest_path, self._strategy_label())
                moved += 1
            except (PermissionError, OSError) as e:
                print(f"  {Fore.RED}移动失败: {f.path} ({e}){Style.RESET_ALL}")

        logger.log_summary(len(self.files), moved)
        log_path = logger.save()

        self._cleanup_empty_dirs()

        print(f"\n{Fore.GREEN}归档完成! 移动了 {moved} 个文件。{Style.RESET_ALL}")
        print(f"日志已保存: {log_path}")
        return moved

    def _compute_destination(self, f: FileInfo) -> Path | None:
        """根据策略计算文件的目标目录"""
        if self.strategy == self.STRATEGY_TIME:
            year = f.modified_time.strftime("%Y")
            month = f.modified_time.strftime("%m")
            return self.output_dir / year / month

        elif self.strategy == self.STRATEGY_TYPE:
            return self.output_dir / f.category

        return None

    def _strategy_label(self) -> str:
        if self.strategy == self.STRATEGY_TIME:
            return "按时间 (年/月)"
        elif self.strategy == self.STRATEGY_TYPE:
            return "按文件类型"
        return self.strategy

    def _cleanup_empty_dirs(self):
        """清理归档后产生的空目录"""
        for dirpath in sorted(self.target_dir.rglob("*"), reverse=True):
            if dirpath.is_dir():
                try:
                    if not any(dirpath.iterdir()):
                        if dirpath.name not in ("_backup",):
                            dirpath.rmdir()
                except (PermissionError, OSError):
                    pass
