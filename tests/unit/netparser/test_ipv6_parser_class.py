"""
Unit tests for the `rewordapp.netparser.IPv6Parser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/netparser/test_ipv6_parser.py
    or
    $ python -m pytest tests/unit/netparser/test_ipv6_parser.py
"""

import pytest
from rewordapp.netparser import IPv6Parser


@pytest.mark.parametrize(
    "network",
    [
        "::",
        "::a",
        "::a:b:c",
        "2701:946:200:8c1e::2dd0",
        "fe80::4ec0:79ff:fedd:d656%5",
        "2601:646:8200:8c1e:dd99:4c3f:4edc:ac40"
    ],
)
def test_generate_new_method(network):
    parser = IPv6Parser(network)
    new_parser = parser.generate_new()
    if parser.value == 0:
        assert new_parser.value == 0
    else:
        if parser.octets.total_nonzero_octet() == 1:
            assert parser.octets.first_nonzero_octet() != new_parser.octets.first_nonzero_octet()
        else:
            pivot = parser.octets.first_nonzero_octet().position
            assert parser.octets.get_octet(pivot) == new_parser.octets.get_octet(pivot)
            for index in range(pivot + 1, 8):
                if parser.octets.get_octet(index).value > 0:
                    assert parser.octets.get_octet(index) != new_parser.octets.get_octet(index)


def test_generate_new_method_with_source_parser():

    source_parsers = []

    for addr in [
        "2701:946:200:8c1e::2dd0",
        "2601:646:2a0:8c1e::ac40"
    ]:
        parser = IPv6Parser(addr)
        parser.generate_new(source_parsers=source_parsers)
        source_parsers.append(parser)

    other = IPv6Parser("2701:646:2a0:8c1e::2dd0")
    other.generate_new(source_parsers=source_parsers)

    expects = [
        (True, False, False, True, True, True, True, True),
        (False, True, True, True, True, True, True, False),
    ]

    for index, expect in enumerate(expects):
        source = source_parsers[index]
        for pos in range(8):
            is_equal = source.new_parser.octets.get_octet(pos) == other.new_parser.octets.get_octet(pos)
            assert is_equal == expect[pos]
