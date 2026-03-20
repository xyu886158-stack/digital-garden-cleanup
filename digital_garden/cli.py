"""命令行接口 — 支持 check / deduplicate / archive 子命令"""

import argparse
import io
import sys
from pathlib import Path

from colorama import init as colorama_init

from .archiver import Archiver
from .deduplicator import Deduplicator
from .scanner import DirectoryScanner


def cmd_check(args):
    """扫描目录并报告混乱程度"""
    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"错误: 目录不存在 — {target}")
        sys.exit(1)
    scanner = DirectoryScanner(target)
    scanner.report()


def cmd_deduplicate(args):
    """识别并处理重复文件"""
    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"错误: 目录不存在 — {target}")
        sys.exit(1)

    backup = Path(args.backup).resolve() if args.backup else None
    dedup = Deduplicator(target, backup_dir=backup)
    dedup.find_duplicates()
    dedup.execute(auto_confirm=args.yes)


def cmd_archive(args):
    """智能归档文件"""
    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"错误: 目录不存在 — {target}")
        sys.exit(1)

    output = Path(args.output).resolve() if args.output else None
    archiver = Archiver(target, output_dir=output, strategy=args.strategy)
    archiver.analyze()

    if args.dry_run:
        archiver.show_plan()
    else:
        archiver.execute(auto_confirm=args.yes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="digital-garden",
        description="Digital Garden Clean-up — 个人文件自动化整理助手",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # check
    p_check = subparsers.add_parser("check", help="扫描目录并报告混乱程度")
    p_check.add_argument("directory", help="要扫描的目录路径")
    p_check.set_defaults(func=cmd_check)

    # deduplicate
    p_dedup = subparsers.add_parser("deduplicate", help="识别并处理重复文件")
    p_dedup.add_argument("directory", help="要扫描的目录路径")
    p_dedup.add_argument("--backup", help="备份目录路径（默认: 目标目录/_backup/duplicates）")
    p_dedup.add_argument("-y", "--yes", action="store_true", help="跳过确认，直接执行")
    p_dedup.set_defaults(func=cmd_deduplicate)

    # archive
    p_archive = subparsers.add_parser("archive", help="智能归档文件")
    p_archive.add_argument("directory", help="要归档的目录路径")
    p_archive.add_argument("--output", help="归档输出目录（默认: 原目录内归档）")
    p_archive.add_argument("--strategy", choices=["time", "type"], default="time",
                           help="归档策略: time=按年/月, type=按文件类型 (默认: time)")
    p_archive.add_argument("--dry-run", action="store_true", help="仅预览方案，不执行")
    p_archive.add_argument("-y", "--yes", action="store_true", help="跳过确认，直接执行")
    p_archive.set_defaults(func=cmd_archive)

    return parser


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )
    colorama_init()
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
