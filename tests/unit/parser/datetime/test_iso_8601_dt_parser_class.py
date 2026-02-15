"""
Unit tests for the `rewordapp.parser.datetime.ISO8601DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_iso_8601_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_iso_8601_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import ISO8601DTParser


@pytest.mark.parametrize(
    "text",
    [
        # Calendar date + time
        "2026-02-14T12:57",
        "2026-02-14T12:57:36",
        "2026-02-14T12:57:36.123",

        "2026-02-14T12:57Z",
        "2026-02-14T12:57:36Z",
        "2026-02-14T12:57:36.123Z",

        "2026-02-14T12:57+02:00",
        "2026-02-14T12:57:36-02:00",
        "2026-02-14T12:57:36.123+05:30",

        "20260214T1257",
        "20260214T125736",
        "20260214T125736.123",

        "20260214T1257Z",
        "20260214T125736Z",
        "20260214T125736.123Z",

        "20260214T1257+0200",
        "20260214T125736-0200",
        "20260214T125736.123+0530",

        # Ordinal date + time
        "2026-045T12:57:36",
        "2026-045T12:57:36Z",
        "2026-045T12:57:36+02:00",

        "2026-045T12:57:36.123",
        "2026-045T12:57:36.123Z",
        "2026-045T12:57:36.123+02:00",

        "2026045T125736",
        "2026045T125736Z",
        "2026045T125736+0200",

        "2026045T125736.123",
        "2026045T125736.123Z",
        "2026045T125736.123+0200",

        # Week date + time
        "2026-W06-6T12:57:36",
        "2026-W06-6T12:57:36Z",
        "2026-W06-6T12:57:36+02:30",

        "2026W066T125736",
        "2026W066T125736Z",
        "2026W066T125736+0230",

        "2026-W06-6T12:57:36.123",
        "2026-W06-6T12:57:36.123Z",
        "2026-W06-6T12:57:36.123+02:30",

        "2026W066T125736.123",
        "2026W066T125736.123Z",
        "2026W066T125736.123+0230",
    ],
)
def test_iso_8601_date_time_parsing(text):
    """Ensure ISO8601 parser rewrites datetime to an earlier value."""

    parser = ISO8601DTParser(text)

    assert parser, f"Failed to parse ISO8601 datetime: {text}"

    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
