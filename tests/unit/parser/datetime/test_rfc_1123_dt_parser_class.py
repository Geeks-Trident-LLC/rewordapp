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
    "text, pattern",
    [
        ("Sat, 07 Feb 2026 12:57:36 GMT", "%a, %d %b %Y %H:%M:%S GMT"),
    ],
)
def test_rfc1123_parsing(text, pattern):
    """Ensure RFC1123 parser rewrites datetime to an earlier value."""
    parser = RFC1123DTParser(text)

    assert parser, f"Failed to parse RFC1123 datetime: {text}"

    rewritten = parser.rewritten

    try:
        original_dt = datetime.strptime(text, pattern)
        rewritten_dt = datetime.strptime(rewritten, pattern)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")

    assert original_dt > rewritten_dt, (
        f"Rewritten datetime should be earlier.\n"
        f"Original:  {original_dt}\n"
        f"Rewritten: {rewritten_dt}"
    )
