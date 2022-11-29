# datasette-ephemeral-tables

[![PyPI](https://img.shields.io/pypi/v/datasette-ephemeral-tables.svg)](https://pypi.org/project/datasette-ephemeral-tables/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-ephemeral-tables?include_prereleases&label=changelog)](https://github.com/simonw/datasette-ephemeral-tables/releases)
[![Tests](https://github.com/simonw/datasette-ephemeral-tables/workflows/Test/badge.svg)](https://github.com/simonw/datasette-ephemeral-tables/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-ephemeral-tables/blob/main/LICENSE)

Provide tables that expire after a time limit

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-ephemeral-tables

## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-ephemeral-tables
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
