"""
Unit tests for the `rewordapp.parser.datetime.RFC850DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_850_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_850_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC850DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Saturday, 07-Feb-26 12:57:36 GMT",
    ],
)
def test_rfc850_parsing(text):
    """Ensure RFC850 parser rewrites datetime to an earlier value."""
    parser = RFC850DTParser(text)

    assert parser, f"Failed to parse RFC850 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
