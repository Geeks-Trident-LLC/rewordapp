"""
Unit tests for the `rewordapp.parser.datetime.ISO8601DTParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/datetime/test_iso_8601_dt_parser_class.py
    or
    $ python -m pytest tests/unit/parser/datetime/test_iso_8601_dt_parser_class.py
"""

import pytest
from datetime import datetime

from rewordapp.parser.datetime import ISO8601DTParser


@pytest.mark.parametrize(
    "text, pattern",
    [
        # Calendar date + time
        ("2026-02-14T12:57", "%Y-%m-%dT%H:%M"),
        ("2026-02-14T12:57:36", "%Y-%m-%dT%H:%M:%S"),
        ("2026-02-14T12:57:36.123", "%Y-%m-%dT%H:%M:%S.%f"),

        ("2026-02-14T12:57Z", "%Y-%m-%dT%H:%M%z"),
        ("2026-02-14T12:57:36Z", "%Y-%m-%dT%H:%M:%S%z"),
        ("2026-02-14T12:57:36.123Z", "%Y-%m-%dT%H:%M:%S.%f%z"),

        ("2026-02-14T12:57+02:00", "%Y-%m-%dT%H:%M%z"),
        ("2026-02-14T12:57:36-02:00", "%Y-%m-%dT%H:%M:%S%z"),
        ("2026-02-14T12:57:36.123+05:30", "%Y-%m-%dT%H:%M:%S.%f%z"),

        ("20260214T1257", "%Y%m%dT%H%M"),
        ("20260214T125736", "%Y%m%dT%H%M%S"),
        ("20260214T125736.123", "%Y%m%dT%H%M%S.%f"),

        ("20260214T1257Z", "%Y%m%dT%H%M%z"),
        ("20260214T125736Z", "%Y%m%dT%H%M%S%z"),
        ("20260214T125736.123Z", "%Y%m%dT%H%M%S.%f%z"),

        ("20260214T1257+0200", "%Y%m%dT%H%M%z"),
        ("20260214T125736-0200", "%Y%m%dT%H%M%S%z"),
        ("20260214T125736.123+0530", "%Y%m%dT%H%M%S.%f%z"),

        # Ordinal date + time
        ("2026-045T12:57:36", "%Y-%jT%H:%M:%S"),
        ("2026-045T12:57:36Z", "%Y-%jT%H:%M:%S%z"),
        ("2026-045T12:57:36+02:00", "%Y-%jT%H:%M:%S%z"),

        ("2026-045T12:57:36.123", "%Y-%jT%H:%M:%S.%f"),
        ("2026-045T12:57:36.123Z", "%Y-%jT%H:%M:%S.%f%z"),
        ("2026-045T12:57:36.123+02:00", "%Y-%jT%H:%M:%S.%f%z"),

        ("2026045T125736", "%Y%jT%H%M%S"),
        ("2026045T125736Z", "%Y%jT%H%M%S%z"),
        ("2026045T125736+0200", "%Y%jT%H%M%S%z"),

        ("2026045T125736.123", "%Y%jT%H%M%S.%f"),
        ("2026045T125736.123Z", "%Y%jT%H%M%S.%f%z"),
        ("2026045T125736.123+0200", "%Y%jT%H%M%S.%f%z"),

        # Week date + time
        ("2026-W06-6T12:57:36", "%G-W%V-%uT%H:%M:%S"),
        ("2026-W06-6T12:57:36Z", "%G-W%V-%uT%H:%M:%S%z"),
        ("2026-W06-6T12:57:36+02:30", "%G-W%V-%uT%H:%M:%S%z"),

        ("2026W066T125736", "%GW%V%uT%H%M%S"),
        ("2026W066T125736Z", "%GW%V%uT%H%M%S%z"),
        ("2026W066T125736+0230", "%GW%V%uT%H%M%S%z"),

        ("2026-W06-6T12:57:36.123", "%G-W%V-%uT%H:%M:%S.%f"),
        ("2026-W06-6T12:57:36.123Z", "%G-W%V-%uT%H:%M:%S.%f%z"),
        ("2026-W06-6T12:57:36.123+02:30", "%G-W%V-%uT%H:%M:%S.%f%z"),

        ("2026W066T125736.123", "%GW%V%uT%H%M%S.%f"),
        ("2026W066T125736.123Z", "%GW%V%uT%H%M%S.%f%z"),
        ("2026W066T125736.123+0230", "%GW%V%uT%H%M%S.%f%z"),


    ],
)
def test_iso_8601_date_time_parsing(text, pattern):
    """Ensure ISO8601 parser rewrites datetime to an earlier value."""

    parser = ISO8601DTParser(text)

    assert parser, f"Failed to parse ISO8601 datetime: {text}"

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
