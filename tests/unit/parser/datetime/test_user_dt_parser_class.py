"""
Unit tests for the `rewordapp.parser.datetime.UserDTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_user_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_user_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import UserDTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sunday 8 PM",
        "Sun 8 pm",
        "Sunday 8PM",
        "Sun 8pm",

        "02-15-2026 8PM",
        "02-15-2026 8 PM",
        "02-15-2026 08:30 PM",
        "02-15-2026 08:30:40 PM",
        "02-15-2026 08:30:40.123 PM",
        "02-15-2026 08:30:40.123 PM +02:30",
        "02-15-2026 08:30:40.123 PM UTC",

        "02/15/2026 8PM",
        "02/15/2026 8 PM",
        "02/15/2026 08:30 PM",
        "02/15/2026 08:30:40 PM",
        "02/15/2026 08:30:40.123 PM",
        "02/15/2026 08:30:40.123 PM +02:30",
        "02/15/2026 08:30:40.123 PM UTC",

        "February 15, 2026 8PM",
        "Feb 15, 2026 8 PM",
        "Feb 15, 2026 08:30 PM",
        "February 15, 2026 08:30:40 PM",
        "February 15, 2026 08:30:40.123 PM +02:30",
        "February 15, 2026 08:30:40.123 PM UTC",

        "Sunday, February 15, 2026 8PM",
        "Sun, Feb 15, 2026 8 PM",
        "Sun, Feb 15, 2026 08:30 PM",
        "Sunday, February 15, 2026 08:30:40 PM",
        "Sunday, February 15, 2026 08:30:40.123 PM +02:30",
        "Sunday, February 15, 2026 08:30:40.123 PM UTC",
    ],
)
def test_user_datetime_12h_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""
    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        # Mon-Day
        "Feb 15, 2026 08:30",
        "February 15, 2026 08:30:40",
        "February 15, 2026 08:30:40.123",
        "February 15, 2026 08:30:40.123 +02:30",
        "Feb 15, 2026 08:30:40.123 UTC",

        # Weekday-Month-Day
        "Sun, Feb 15, 2026 08:30",
        "Sunday, February 15, 2026 08:30:40",
        "Sunday, February 15, 2026 08:30:40.123",
        "Sun, Feb 15, 2026 08:30:40.123 +02:30",
        "Sunday, February 15, 2026 08:30:40.123 UTC",

        # Day-Month
        "15 Feb 2026 08:30",
        "15 Feb 2026 08:30:40",
        "15 Feb 2026 08:30:40.123",
        "15 Feb 2026 08:30:40.123 +02:30",
        "15 Feb 2026 08:30:40.123 UTC",

    ],
)
def test_user_datetime_other_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""
    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        # YYYYMMDD HHMM..
        "20260215 08:30",
        "20260215 08:30:40",
        "20260215 08:30:40.123",
        "20260215 08:30:40.123 +02:30",
        "20260215 08:30:40.123 UTC",

        # # YYYYMMDDHHMM..
        "202602150830",
        "20260215083040",
        "20260215083040.123",
        "20260215083040.123+02:30",
        "20260215083040.123UTC",
    ],
)
def test_user_datetime_compact_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""
    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "02-15-2026 08:30",
        "02-15-2026 08:30:40",
        "02-15-2026 08:30:40.123",

        "02-15-2026 08:30 +02:30",
        "02-15-2026 08:30:40 +02:30",
        "02-15-2026 08:30:40.123 +02:30",

        "02-15-2026 08:30 UTC",
        "02-15-2026 08:30:40 UTC",
        "02-15-2026 08:30:40.123 UTC",

        "02/15/2026 08:30",
        "02/15/2026 08:30:40",
        "02/15/2026 08:30:40.123",

        "02/15/2026 08:30 +02:30",
        "02/15/2026 08:30:40 +02:30",
        "02/15/2026 08:30:40.123 +02:30",

        "02/15/2026 08:30 UTC",
        "02/15/2026 08:30:40 UTC",
        "02/15/2026 08:30:40.123 UTC",
    ],
)
def test_user_datetime_us_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""
    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "15-02-2026 08:30",
        "15-02-2026 08:30:40",
        "15-02-2026 08:30:40.123",

        "15-02-2026 08:30 +02:30",
        "15-02-2026 08:30:40 +02:30",
        "15-02-2026 08:30:40.123 +02:30",

        "15-02-2026 08:30 UTC",
        "15-02-2026 08:30:40 UTC",
        "15-02-2026 08:30:40.123 UTC",

        "15/02/2026 08:30",
        "15/02/2026 08:30:40",
        "15/02/2026 08:30:40.123",

        "15/02/2026 08:30 +02:30",
        "15/02/2026 08:30:40 +02:30",
        "15/02/2026 08:30:40.123 +02:30",

        "15/02/2026 08:30 UTC",
        "15/02/2026 08:30:40 UTC",
        "15/02/2026 08:30:40.123 UTC",

        "15.02.2026 08:30",
        "15.02.2026 08:30:40",
        "15.02.2026 08:30:40.123",

        "15.02.2026 08:30 +02:30",
        "15.02.2026 08:30:40 +02:30",
        "15.02.2026 08:30:40.123 +02:30",

        "15.02.2026 08:30 UTC",
        "15.02.2026 08:30:40 UTC",
        "15.02.2026 08:30:40.123 UTC",
    ],
)
def test_user_datetime_european_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""

    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "2026-02-15 08:30",
        "2026-02-15 08:30:40",
        "2026-02-15 08:30:40.123",
        "2026-02-15 08:30:40.123 +02:30",
        "2026-02-15 08:30:40.123 UTC",

        "2026/02/15 08:30",
        "2026/02/15 08:30:40",
        "2026/02/15 08:30:40.123",
        "2026/02/15 08:30:40.123 +02:30",
        "2026/02/15 08:30:40.123 UTC",

        "2026.02.15 08:30",
        "2026.02.15 08:30:40",
        "2026.02.15 08:30:40.123",
        "2026.02.15 08:30:40.123 +02:30",
        "2026.02.15 08:30:40.123 UTC",
    ],
)
def test_user_datetime_iso_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""

    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "2026-W07-6 08:30",
        "2026-W07-6 08:30:40",
        "2026-W07-6 08:30:40.123",
        "2026-W07-6 08:30:40.123 +02:30",
        "2026-W07-6 08:30:40.123 UTC",

        "2026W076 0830",
        "2026W076 083040",
        "2026W076 083040.123",
        "2026W076 083040.123 +0230",
        "2026W076 083040.123 UTC",
    ],
)
def test_user_datetime_iso_week_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""

    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")


@pytest.mark.parametrize(
    "text",
    [
        "2026-045 08:30",
        "2026-045 08:30:40",
        "2026-045 08:30:40.123",
        "2026-045 08:30:40.123 +02:30",
        "2026-045 08:30:40.123 UTC",

        "2026045 0830",
        "2026045 083040",
        "2026045 083040.123",
        "2026045 083040.123 +0230",
        "2026045 083040.123 UTC",
    ],
)
def test_user_datetime_iso_ordinal_style_parsing(text):
    """Ensure user parser rewrites datetime to an earlier value."""

    parser = UserDTParser(text)

    assert parser, f"Failed to parse User datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")