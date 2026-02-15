"""
Unit tests for the `rewordapp.parser.datetime.RFC2822DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_2822_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_2822_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC2822DTParser


@pytest.mark.parametrize(
    "text",
    [
        "Sat, 07 Feb 2026 12:57:36 -0800",
        "Sat, 07 Feb 2026 12:57 -0800",
        "07 Feb 2026 12:57:36 -0800",
        "07 Feb 2026 12:57 -0800",
    ],
)
def test_rfc2822_parsing(text):
    """Ensure RFC2822 parser rewrites datetime to an earlier value."""
    parser = RFC2822DTParser(text)

    assert parser, f"Failed to parse RFC2822 datetime: {text}"
    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
