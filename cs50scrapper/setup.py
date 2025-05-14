from setuptools import setup, find_packages

setup(
    name="cs50scrapper",
    version="0.1.0",
    description="Generic CS50 course page scraper",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "cs50scrapper=cs50scrapper.cli:main",
        ],
    },
    python_requires=">=3.6",
)
