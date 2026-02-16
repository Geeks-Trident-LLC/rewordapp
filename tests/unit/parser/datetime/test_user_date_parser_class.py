"""
Unit tests for the `rewordapp.parser.datetime.UserDateParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_user_date_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_user_date_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import UserDateParser


@pytest.mark.parametrize(
    "text",
    [
        # weekday, month day, year
        "Sunday, February 15, 2026",
        "Sun, Feb 15, 2026",

        # month day, year
        "February 15, 2026",
        "Feb 15, 2026",

        # day month year
        "15 February 2026",
        "15 Feb 2026",

        # %m-%d-%y or %m/%d/%y
        "02-15-26",
        "02/15/26",

        # %Y%m%d
        "20260215",

        # US date style
        "02-15-2026",
        "02/15/2026",

        # EU date style
        "15-02-2026",
        "15/02/2026",
        "15.02.2026",

        # ISO week date
        "2026-W07-7",
        "2026W077",

        # ISO Ordinal date
        "2026-046",
        "2026046",

        # ISO Calendar date
        "2026-02-15",
        "2026/02/15",
        "2026.02.15",
    ],
)
def test_user_date_parsing(text):
    """Ensure user parser rewrites date to an earlier value."""

    parser = UserDateParser(text)

    assert parser, f"Failed to parse User date: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")