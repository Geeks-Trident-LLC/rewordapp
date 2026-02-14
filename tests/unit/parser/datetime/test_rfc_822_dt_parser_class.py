"""
Unit tests for the `rewordapp.parser.datetime` module.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_822_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_822_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC822DTParser


@pytest.mark.parametrize(
    "text, pattern",
    [
        ("07 Feb 82 12:57:45 GMT", "%d %b %y %H:%M:%S GMT"),
        ("Sat, 07 Feb 82 12:57:36 GMT", "%a, %d %b %y %H:%M:%S GMT"),
        ("07 Feb 82 12:57 GMT", "%d %b %y %H:%M GMT"),
        ("Sat, 07 Feb 82 12:57 GMT", "%a, %d %b %y %H:%M GMT"),
    ],
)
def test_rfc822_parsing(text, pattern):
    """Ensure RFC822 parser rewrites datetime to an earlier value."""
    parser = RFC822DTParser(text)

    assert parser, f"Failed to parse RFC822 datetime: {text}"

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
