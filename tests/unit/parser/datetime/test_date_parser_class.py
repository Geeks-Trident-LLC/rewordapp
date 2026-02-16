"""
Unit tests for the `rewordapp.parser.datetime.DateParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_date_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_date_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import DateParser


@pytest.mark.parametrize(
    "text",
    [
        # weekday, month day, year
        "Sunday, February 15, 2026",
        "*****Sun, Feb 15, 2026======",

        # month day, year
        "February 15, 2026",
        "(Feb 15, 2026,",

        # day month year
        "15 February 2026",
        "15 Feb 2026",

        # %m-%d-%y or %m/%d/%y
        "02-15-26",
        "02/15/26",
    ],
)
def test_date_parsing(text):
    parser = DateParser(text)

    assert parser, f"Failed to parse date: {text}"

    try:
        datetime.strptime(text, parser.output_format)
        datetime.strptime(parser.rewritten, parser.output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
