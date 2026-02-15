"""
Unit tests for the `rewordapp.parser.datetime.ISO8601DateParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_iso_8601_date_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_iso_8601_date_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import ISO8601DateParser


@pytest.mark.parametrize(
    "text, pattern",
    [
        # Calendar date + time
        ("2026-02-14", "%Y-%m-%d"),
        ("20260214", "%Y%m%d"),

        # Ordinal date + time
        ("2026-045", "%Y-%j"),
        ("2026045", "%Y%j"),
        #
        # Week date + time
        ("2026-W06-6", "%G-W%V-%u"),
        ("2026W066", "%GW%V%u"),


    ],
)
def test_iso_8601_date_parsing(text, pattern):
    """Ensure ISO8601 parser rewrites date to an earlier value."""

    parser = ISO8601DateParser(text)

    assert parser, f"Failed to parse ISO8601 date: {text}"

    rewritten = parser.rewritten

    try:
        original_dt = datetime.strptime(text, pattern)
        rewritten_dt = datetime.strptime(rewritten, pattern)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")

    assert original_dt > rewritten_dt, (
        f"Rewritten date should be earlier.\n"
        f"Original:  {original_dt}\n"
        f"Rewritten: {rewritten_dt}"
    )
