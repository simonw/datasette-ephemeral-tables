from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-demo-database",
    description="Configure in-memory demo databases for Datasette",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-demo-database",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-demo-database/issues",
        "CI": "https://github.com/simonw/datasette-demo-database/actions",
        "Changelog": "https://github.com/simonw/datasette-demo-database/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License"
    ],
    version=VERSION,
    packages=["datasette_demo_database"],
    entry_points={"datasette": ["demo_database = datasette_demo_database"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
