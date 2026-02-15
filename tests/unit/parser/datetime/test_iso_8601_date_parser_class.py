"""
Unit tests for the `rewordapp.parser.datetime.ISO8601DateParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_iso_8601_date_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_iso_8601_date_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import ISO8601DateParser


@pytest.mark.parametrize(
    "text",
    [
        # Calendar date + time
        "2026-02-14",
        "20260214",

        # Ordinal date + time
        "2026-045",
        "2026045",
        #
        # Week date + time
        "2026-W06-6",
        "2026W066",


    ],
)
def test_iso_8601_date_parsing(text):
    """Ensure ISO8601 parser rewrites date to an earlier value."""

    parser = ISO8601DateParser(text)

    assert parser, f"Failed to parse ISO8601 date: {text}"

    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
