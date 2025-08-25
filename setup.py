#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for emacs-tracker
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="emacs-tracker",
    version="0.1.0",
    author="Yusuke Watanabe",
    author_email="Yusuke.Watanabe@scitex.ai",
    description="MCP server for tracking Emacs user interaction context and behavioral patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ywatanabe/emacs-tracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Editors :: Emacs",
        "Topic :: System :: Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",  # Model Context Protocol
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "emacs-tracker=emacs_tracker.server:main",
        ],
    },
    keywords="emacs user-interaction mcp context",
)
