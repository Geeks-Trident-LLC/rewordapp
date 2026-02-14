"""
Unit tests for the `rewordapp.parser.datetime.RFC7231DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_2822_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_7231_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC7231DTParser


@pytest.mark.parametrize(
    "text, pattern",
    [
        ("Sat, 07 Feb 2026 12:57:36 GMT", "%a, %d %b %Y %H:%M:%S GMT"),
        ("Saturday, 07-Feb-26 12:57:36 GMT", "%A, %d-%b-%y %H:%M:%S GMT"),
        ("Sat Feb  7 12:57:36 2026", "%a %b %d %H:%M:%S %Y"),
    ],
)
def test_rfc7231_parsing(text, pattern):
    """Ensure RFC7231 parser rewrites datetime to an earlier value."""
    parser = RFC7231DTParser(text)

    assert parser, f"Failed to parse RFC7231 datetime: {text}"

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
