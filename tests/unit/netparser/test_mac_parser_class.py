"""
Unit tests for the `rewordapp.netparser.MacParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/netparser/test_mac_parser.py
    or
    $ python -m pytest tests/unit/netparser/test_mac_parser.py
"""

import pytest
from rewordapp.netparser import MACParser


@pytest.mark.parametrize(
    "txt, expected",
    [
        ("00:1A:2B:3C:4D:5E", ("00:1A:2B:3C:4D:5E", "", "")),
        ("00-1A-2B-3C-4D-5E", ("00-1A-2B-3C-4D-5E", "", "")),
        ("001.A2B.3C4.D5E", ("001.A2B.3C4.D5E", "", "")),
        ("001A2B3C4D5E", ("001A2B3C4D5E", "", "")),

        ("00:1A:2B:3C:4D:5E,", ("00:1A:2B:3C:4D:5E", "", ",")),
        ("(00:1A:2B:3C:4D:5E", ("00:1A:2B:3C:4D:5E", "(", "")),

    ],
)
def test_mac_parser_initialization(txt, expected):
    """Ensure MACParser extracts address, prefix, and suffix correctly."""
    exp_addr, exp_prefix, exp_suffix = expected
    parser = MACParser(txt)
    assert parser.address == exp_addr
    assert parser.prefix == exp_prefix
    assert parser.suffix == exp_suffix


@pytest.mark.parametrize(
    "txt",
    [
        "00:00:00:00:00:00",
        "FF:FF:FF:FF:FF:FF",
        "00:1A:2B:3C:4D:5E",
        "00-1A-2B-3C-4D-5E",
        "001.A2B.3C4.D5E",
        "001A2B3C4D5E",
    ],
)
def test_generate_new(txt):
    """Verify generate_new() preserves or changes octets as expected."""
    parser = MACParser(txt)
    new_parser = parser.generate_new()
    if parser.value in [0, int("f" * 12, 16)]:
        assert new_parser.value == parser.value
    else:
        assert new_parser.address.startswith(parser.address[:len(parser.address)//2])
        assert new_parser.value != parser.value
