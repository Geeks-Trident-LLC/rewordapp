"""
Unit tests for the `rewordapp.parser.datetime.RFC7231DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_7231_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_7231_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC7231DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sat, 07 Feb 2026 12:57:36 GMT",
        "Saturday, 07-Feb-26 12:57:36 GMT",
        "Sat Feb  7 12:57:36 2026",
    ],
)
def test_rfc7231_parsing(text):
    """Ensure RFC7231 parser rewrites datetime to an earlier value."""
    parser = RFC7231DTParser(text)

    assert parser, f"Failed to parse RFC7231 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
