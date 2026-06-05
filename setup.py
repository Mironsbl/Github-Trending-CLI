"""pip-installable package configuration for github-trending-cli."""

from setuptools import setup, find_packages

setup(
    name="github-trending-cli",
    version="3.0.0",
    description="🔥 A powerful CLI to fetch and display trending GitHub repositories.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AIwolfie",
    url="https://github.com/AIwolfie/Github-Trending-CLI",
    license="MIT",
    py_modules=["main", "github_api", "utils", "scraper", "web"],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "github-trending=main:main",
            "gt=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries",
    ],
)
