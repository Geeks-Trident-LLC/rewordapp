"""
Unit tests for the `rewordapp.parser.datetime.TimeParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_time_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_time_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import TimeParser


@pytest.mark.parametrize(
    "text",
    [
        "*****08:30:40.123 PM++++++",
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
    ],
)
def test_time_parsing(text):
    parser = TimeParser(text)

    assert parser, f"Failed to parse time: {text}"

    try:
        datetime.strptime(text, parser.output_format)
        datetime.strptime(parser.rewritten, parser.output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
