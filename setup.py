"""Setup configuration for reddit-pain CLI tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reddit-pain",
    version="1.0.0",
    author="minirr890112-byte",
    description="Reddit Pain Workflow — scan developer subreddits for pain signals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
    ],
    py_modules=["reddit_pain_workflow"],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "reddit-pain=reddit_pain.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
