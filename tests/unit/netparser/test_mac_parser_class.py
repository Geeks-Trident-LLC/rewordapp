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

        (". . .00:1A:2B:3C:4D:5E,", ("00:1A:2B:3C:4D:5E", ". . .", ",")),
        ("(00:1A:2B:3C:4D:5E, ...", ("00:1A:2B:3C:4D:5E", "(", ", ...")),

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
def test_generate_new_basic_behavior(txt):
    """Verify generate_new() preserves or changes octets as expected."""
    parser = MACParser(txt)
    new_parser = parser.generate_new()
    if parser.value in [0, int("f" * 12, 16)]:
        assert new_parser.value == parser.value
    else:
        half = len(parser.octets) // 2
        for index, octet in enumerate(parser.octets.octets):
            if index < half:
                assert new_parser.octets.get_octet(index) == octet
            else:
                assert new_parser.octets.get_octet(index) != octet



def test_generate_new_method_with_source_parser():
    """Ensure octet syncing works when source parsers are provided."""
    source_parsers = []

    for addr in [
        "11:22:33:aa:bb:cc",
        "44-55-66-dd-ee-ff",
        "aabb331234dd",
        "11:55:33:aa:ee:dd"
    ]:
        parser = MACParser(addr)
        parser.generate_new(source_parsers=source_parsers)
        source_parsers.append(parser)

    other = MACParser("11:55:33:aa:ee:dd")
    other.generate_new(source_parsers=source_parsers)

    expects = [
        (True, False, True, True, False, False),
        (False, True, False, False, True, False),
        (False, False, True, False, False, True),
        (True, True, True, True, True, True)
    ]

    for index, expect in enumerate(expects):
        source = source_parsers[index]
        for pos in range(len(other.network_info.octets)):
            is_equal = source.new_parser.octets.get_octet(pos) == other.new_parser.octets.get_octet(pos)
            assert is_equal == expect[pos]
