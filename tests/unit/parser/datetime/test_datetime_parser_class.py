"""
Unit tests for the `rewordapp.parser.datetime.DateTimeParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_datetime_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_datetime_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import DateTimeParser


@pytest.mark.parametrize(
    "text",
    [
        # Mon-Day
        "-----Feb 15, 2026 08:30.....",
        "February 15, 2026 08:30:40",
        "February 15, 2026 08:30:40.123",
        "February 15, 2026 08:30:40.123 +02:30",
        "Feb 15, 2026 08:30:40.123 UTC",

        # Weekday-Month-Day
        "Sun, Feb 15, 2026 08:30",
        "Sunday, February 15, 2026 08:30:40",

        # Day-Month
        "15 Feb 2026 08:30",
    ],
)
def test_datetime_parsing(text):
    parser = DateTimeParser(text)

    assert parser, f"Failed to parse datetime: {text}"

    try:
        datetime.strptime(text, parser.output_format)
        datetime.strptime(parser.rewritten, parser.output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
