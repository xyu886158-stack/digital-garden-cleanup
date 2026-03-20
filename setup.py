from setuptools import setup, find_packages

setup(
    name="digital-garden-cleanup",
    version="1.0.0",
    description="个人文件自动化整理助手",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "garden-cleanup=digital_garden.cli:main",
        ],
    },
)
