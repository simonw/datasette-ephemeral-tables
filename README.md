# datasette-demo-database

[![PyPI](https://img.shields.io/pypi/v/datasette-demo-database.svg)](https://pypi.org/project/datasette-demo-database/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-demo-database?include_prereleases&label=changelog)](https://github.com/simonw/datasette-demo-database/releases)
[![Tests](https://github.com/simonw/datasette-demo-database/workflows/Test/badge.svg)](https://github.com/simonw/datasette-demo-database/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-demo-database/blob/main/LICENSE)

Configure in-memory demo databases for Datasette

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-demo-database

## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-demo-database
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
