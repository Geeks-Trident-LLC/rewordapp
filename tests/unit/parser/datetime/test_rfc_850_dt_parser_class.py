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
    "text, pattern",
    [
        ("Saturday, 07-Feb-26 12:57:36 GMT", "%A, %d-%b-%y %H:%M:%S GMT"),
    ],
)
def test_rfc850_parsing(text, pattern):
    """Ensure RFC822 parser rewrites datetime to an earlier value."""
    parser = RFC850DTParser(text)

    assert parser, f"Failed to parse RFC850 datetime: {text}"

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
