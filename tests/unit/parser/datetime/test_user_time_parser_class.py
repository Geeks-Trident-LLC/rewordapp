"""
Unit tests for the `rewordapp.parser.datetime.UserTimeParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_user_time_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_user_time_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import UserTimeParser


@pytest.mark.parametrize(
    "text",
    [
        "08:30:40.123 PM",
        "08:30:40.123 PM +02:30",
        "08:30:40.123 PM UTC",

        "083040.123PM",
        "083040.123PM+0230",
        "083040.123PMUTC",

        "08:30:40 PM",
        "08:30:40 PM +02:30",
        "08:30:40 PM UTC",

        "08:30 PM",
        "08:30 PM +02:30",
        "08:30 PM UTC",

        "8 PM",
        "8PM",
        "0830PM",
        "083040PM",

        "8 PM +02:30",
        "08PM+0230",
        "0830PM+0230",
        "083040PM+0230",

        "08 PM UTC",
        "08PMUTC",
        "0830PMUTC",
        "083040PMUTC",

    ],
)
def test_user_time_12h_style_parsing(text):
    """Ensure user parser rewrites time to an earlier value."""

    parser = UserTimeParser(text)

    assert parser, f"Failed to parse User Time: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "08:30:40.123",
        "08:30:40.123 +02:30",
        "08:30:40.123 UTC",

        "083040.123",
        "083040.123+0230",
        "083040.123UTC",

        "08:30:40",
        "08:30:40 +02:30",
        "08:30:40 UTC",

        "08:30",
        "08:30 +02:30",
        "08:30 UTC",

        "8",
        "0830",
        "083040",

        "08+0230",
        "0830+0230",
        "083040+0230",

        "08UTC",
        "0830UTC",
        "083040UTC",
    ],
)
def test_user_time_24h_style_parsing(text):
    """Ensure user parser rewrites time to an earlier value."""

    parser = UserTimeParser(text)

    assert parser, f"Failed to parse User Time: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")