"""
Unit tests for the `rewordapp.parser.datetime.RFC3339DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_3339_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_3339_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC3339DTParser


@pytest.mark.parametrize(
    "text",
    [
        "2026-02-07T12:57:36Z",
        "2026-02-07T12:57:36-08:00",
        "2026-02-07T12:57:36.123456-08:00",
        "2026-02-07T12:57:36.123456Z",
        "2026-02-07T12:57:36.123Z",
    ],
)
def test_rfc3339_parsing(text):
    """Ensure RFC3339 parser rewrites datetime to an earlier value."""
    parser = RFC3339DTParser(text)

    assert parser, f"Failed to parse RFC3339 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
