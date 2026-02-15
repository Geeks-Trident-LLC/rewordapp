"""
Unit tests for the `rewordapp.parser.datetime.ISO8601TimeParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_iso_8601_time_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_iso_8601_time_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import ISO8601TimeParser


@pytest.mark.parametrize(
    "text",
    [
        "09:30:20.123Z",
        "09:30:20.123+02:30",
        "09:30:20.123",
        "09:30:20",
    ],
)
def test_iso_8601_time_parsing(text):
    """Ensure ISO8601 parser rewrites time to an earlier value."""

    parser = ISO8601TimeParser(text)

    assert parser, f"Failed to parse ISO8601 time: {text}"

    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
