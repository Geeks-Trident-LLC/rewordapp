"""
Unit tests for the `rewordapp.parser.datetime.RFC3339DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_rfc_2822_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_rfc_3339_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import RFC3339DTParser


@pytest.mark.parametrize(
    "text, pattern",
    [
        ("2026-02-07T12:57:36Z", "%Y-%m-%dT%H:%M:%SZ"),
        ("2026-02-07T12:57:36-08:00", "%Y-%m-%dT%H:%M:%S-08:00"),
        ("2026-02-07T12:57:36.123456-08:00", "%Y-%m-%dT%H:%M:%S.123456-08:00"),
        ("2026-02-07T12:57:36.123456Z", "%Y-%m-%dT%H:%M:%S.123456Z"),
        ("2026-02-07T12:57:36.123Z", "%Y-%m-%dT%H:%M:%S.123Z"),
    ],
)
def test_rfc3339_parsing(text, pattern):
    """Ensure RFC3339 parser rewrites datetime to an earlier value."""
    parser = RFC3339DTParser(text)

    assert parser, f"Failed to parse RFC3339 datetime: {text}"

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
