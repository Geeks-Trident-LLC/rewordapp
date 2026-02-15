"""
Unit tests for the `rewordapp.parser.datetime.RFC822DTParser` class.

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
    "text",
    [
        "07 Feb 82 12:57:45 GMT",
        "Sat, 07 Feb 82 12:57:36 GMT",
        "07 Feb 82 12:57 GMT",
        "Sat, 07 Feb 82 12:57 GMT",
    ],
)
def test_rfc822_parsing(text):
    """Ensure RFC822 parser rewrites datetime to an earlier value."""
    parser = RFC822DTParser(text)

    assert parser, f"Failed to parse RFC822 datetime: {text}"

    try:
        datetime.strptime(text, parser._output_format)
        datetime.strptime(parser.rewritten, parser._output_format)
    except Exception as exc:
        pytest.fail(f"strptime failed: {exc}")
