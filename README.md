# Digital Garden Clean-up 🌿

个人文件自动化整理助手 — 通过 AI 识别文件属性、处理重复内容，并建立一套自动化、务实的归档体系。

## 功能特性

- **`check`** — 扫描目录，报告混乱程度（重复文件数、长期未访问文件、文件类型分布）
- **`deduplicate`** — 基于 SHA-256 哈希校验精准识别重复文件，保留一份，其余安全转移至备份目录
- **`archive`** — 按"年份/月份"或"文件类型"进行智能归档

## 安全承诺

- **永不直接删除**：所有"清理"操作实际是移动到 `_backup/` 目录
- **操作前确认**：任何文件移动前都会输出清单并请求用户确认
- **完整日志**：每次操作自动生成 `organized_log.md` 记录搬迁痕迹
- **只移不改**：绝不修改文件内部数据

## 安装

```bash
git clone https://github.com/your-username/digital-garden-cleanup.git
cd digital-garden-cleanup
pip install -r requirements.txt
```

## 使用方法

```bash
# 扫描目录并报告混乱程度
python -m digital_garden check /path/to/your/messy/folder

# 识别并处理重复文件
python -m digital_garden deduplicate /path/to/your/messy/folder

# 智能归档（按时间）
python -m digital_garden archive /path/to/your/messy/folder --strategy time

# 智能归档（按文件类型）
python -m digital_garden archive /path/to/your/messy/folder --strategy type
```

## 归档策略

### 按时间归档 (`--strategy time`)
```
目标目录/
├── 2024/
│   ├── 01/
│   ├── 02/
│   └── ...
├── 2025/
│   ├── 01/
│   └── ...
```

### 按类型归档 (`--strategy type`)
```
目标目录/
├── 文档/
├── 图片/
├── 视频/
├── 音频/
├── 压缩包/
├── 代码/
└── 其他/
```

## 项目结构

```
digital-garden-cleanup/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── digital_garden/
│   ├── __init__.py
│   ├── cli.py          # 命令行入口
│   ├── scanner.py      # 目录扫描 & 混乱度报告
│   ├── deduplicator.py # 重复文件处理
│   ├── archiver.py     # 智能归档引擎
│   ├── logger.py       # 日志生成
│   └── utils.py        # 工具函数
└── tests/
    ├── test_scanner.py
    ├── test_deduplicator.py
    └── test_archiver.py
```

## 技术要求

- Python 3.10+

## 许可证

MIT License
