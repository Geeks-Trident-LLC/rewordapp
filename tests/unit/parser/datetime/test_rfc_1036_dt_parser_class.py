"""
Unit tests for the `rewordapp.parser.datetime.RFC1036DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_1036_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_1036_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC1036DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sat, 07 Feb 2026 12:57:36 GMT",
        "07 Feb 2026 12:57:36 GMT",
    ],
)
def test_rfc1036_parsing(text):
    """Ensure RFC1036 parser rewrites datetime to an earlier value."""
    parser = RFC1036DTParser(text)

    assert parser, f"Failed to parse RFC1036 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
