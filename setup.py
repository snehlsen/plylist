"""Setup configuration for Plylist"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="plylist",
    version="0.1.0",
    author="Plylist Contributors",
    description="A platform-agnostic playlist manager for music streaming services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/plylist",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (none required for base functionality)
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "plylist=plylist.cli.main:main",
        ],
    },
    keywords="playlist music streaming spotify apple-music youtube-music platform-agnostic",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/plylist/issues",
        "Source": "https://github.com/yourusername/plylist",
    },
)
