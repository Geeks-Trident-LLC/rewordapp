"""
Unit tests for the `rewordapp.parser.net.IPv4Parser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/net/test_ipv4_parser.py
    or
    $ python -m pytest tests/unit/parser/net/test_ipv4_parser.py
"""

import pytest
from rewordapp.parser.net import IPv4Parser


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


def test_generate_new():
    """Verify generate_new() preserves or changes octets as expected."""
    parser = IPv4Parser("255.255.255.255")
    new_parser = parser.generate_new()
    assert parser.value == new_parser.value
    parser = IPv4Parser("192.168.0.1")
    new_parser = parser.generate_new()
    assert parser.value != new_parser.value


@pytest.mark.parametrize(
    "original, expected",
    [
        ("10.0.0.1", "10.0.0.1"),
        ("192.168.0.30", "192.168.0.30"),
        ("172.100.90.50/30", "172.100.90.50/28"),
    ],
)
def test_generate_new_produces_identical_values(original, expected):
    """IPv4Parser.generate_new() should yield identical values for identical inputs."""
    parser = IPv4Parser(original)
    other = IPv4Parser(expected)

    assert parser.generate_new().value == other.generate_new().value