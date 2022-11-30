from setuptools import setup
import os

VERSION = "0.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-ephemeral-tables",
    description="Provide tables that expire after a time limit",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-ephemeral-tables",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-ephemeral-tables/issues",
        "CI": "https://github.com/simonw/datasette-ephemeral-tables/actions",
        "Changelog": "https://github.com/simonw/datasette-ephemeral-tables/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["datasette_ephemeral_tables"],
    entry_points={"datasette": ["ephemeral_tables = datasette_ephemeral_tables"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
