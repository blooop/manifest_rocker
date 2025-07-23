#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="dagger-rocker",
    version="0.1.0",
    description="A modern container orchestration tool built on Dagger, inspired by rocker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dagger Rocker Team",
    author_email="team@dagger-rocker.dev",
    url="https://github.com/your-org/dagger-rocker",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "dagger-io>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black",
            "ruff",
        ]
    },
    entry_points={
        "console_scripts": [
            "dagger-rocker=dagger_rocker.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
    ],
)
