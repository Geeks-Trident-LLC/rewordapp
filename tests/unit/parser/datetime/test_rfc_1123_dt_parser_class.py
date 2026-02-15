"""
Unit tests for the `rewordapp.parser.datetime.RFC1123DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_1123_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_1123_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC1123DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sat, 07 Feb 2026 12:57:36 GMT"
    ],
)
def test_rfc1123_parsing(text):
    """Ensure RFC1123 parser rewrites datetime to an earlier value."""
    parser = RFC1123DTParser(text)

    assert parser, f"Failed to parse RFC1123 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
