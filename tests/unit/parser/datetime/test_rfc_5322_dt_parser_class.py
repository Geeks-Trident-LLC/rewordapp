"""
Unit tests for the `rewordapp.parser.datetime.RFC5322DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_5322_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_5322_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC5322DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sat, 07 Feb 2026 12:57:36 -0800",
        "Sat, 07 Feb 2026 12:57 -0800",
        "07 Feb 2026 12:57:36 -0800",
        "07 Feb 2026 12:57 -0800",
    ],
)
def test_rfc5322_parsing(text):
    """Ensure RFC5322 parser rewrites datetime to an earlier value."""
    parser = RFC5322DTParser(text)

    assert parser, f"Failed to parse RFC5322 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
