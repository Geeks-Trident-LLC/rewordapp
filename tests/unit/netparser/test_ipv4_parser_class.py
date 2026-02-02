"""
Unit tests for the `rewordapp.netparser.IPv4Parser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/netparser/test_ipv4_parser.py
    or
    $ python -m pytest tests/unit/netparser/test_ipv4_parser.py
"""

import pytest
from rewordapp.netparser import IPv4Parser


@pytest.mark.parametrize(
    "network, expected",
    [
        ("255.255.255.255", True),
        ("255.255.255.254", True),
        ("255.255.255.252", True),
        ("255.255.255.248", True),
        ("255.255.255.240", True),
        ("255.255.255.224", True),
        ("255.255.255.192", True),
        ("255.255.255.128", True),

        ("255.255.255.0", True),
        ("255.255.254.0", True),
        ("255.255.252.0", True),
        ("255.255.248.0", True),
        ("255.255.240.0", True),
        ("255.255.224.0", True),
        ("255.255.192.0", True),
        ("255.255.128.0", True),

        ("255.255.0.0", True),
        ("255.254.0.0", True),
        ("255.252.0.0", True),
        ("255.248.0.0", True),
        ("255.240.0.0", True),
        ("255.224.0.0", True),
        ("255.192.0.0", True),
        ("255.128.0.0", True),

        ("255.0.0.0", True),
        ("254.0.0.0", True),
        ("252.0.0.0", True),
        ("248.0.0.0", True),
        ("240.0.0.0", True),
        ("224.0.0.0", True),
        ("192.0.0.0", True),
        ("128.0.0.0", True),
    ],
)
def test_valid_netmask_method(network, expected):
    parser = IPv4Parser(network)
    assert parser.is_valid_netmask() == expected


def test_generate_new_basic_behavior():
    """Verify generate_new() preserves or changes octets as expected."""
    parser = IPv4Parser("255.255.255.255")
    new_parse = parser.generate_new()
    assert parser.value == new_parse.value

    parser = IPv4Parser("192.168.0.1")
    new_parser = parser.generate_new()
    assert parser.octets.get_octet(0) == new_parser.octets.get_octet(0)
    assert parser.octets.get_octet(1) != new_parser.octets.get_octet(1)
    assert parser.octets.get_octet(2) == new_parser.octets.get_octet(2)
    assert parser.octets.get_octet(3) != new_parser.octets.get_octet(3)


def test_generate_new_method_with_source_parser():
    """Ensure octet syncing works when source parsers are provided."""
    source_parsers = []

    for addr in [
        "192.168.1.1",
        "192.10.1.30",
        "172.10.20.30",
        "10.0.1.10"
    ]:
        parser = IPv4Parser(addr)
        parser.generate_new(source_parsers=source_parsers)
        source_parsers.append(parser)

    other = IPv4Parser("192.10.1.30")
    other.generate_new(source_parsers=source_parsers)

    expects = [
        (True, False, True, False),
        (True, True, True, True),
        (False, True, False, True),
        (False, False, True, False)
    ]

    for index, expect in enumerate(expects):
        source = source_parsers[index]
        for pos in range(4):
            is_equal = source.new_parser.octets.get_octet(pos) == other.new_parser.octets.get_octet(pos)
            assert is_equal == expect[pos]
