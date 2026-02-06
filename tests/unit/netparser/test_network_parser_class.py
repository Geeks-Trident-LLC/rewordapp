"""
Unit tests for the `rewordapp.netparser.NetParser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/netparser/test_network_parser_class.py
    or
    $ python -m pytest tests/unit/netparser/test_network_parser_class.py
"""

import pytest
from rewordapp.netparser import NetworkParser

@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "1.1.1.1",
            {
                "prefix": "",
                "suffix": "",
                "network": "1.1.1.1",
                "address": "1.1.1.1",
                "subnet": "",
            },
        ),
        (
            "1.1.1.1/32",
            {
                "prefix": "",
                "suffix": "",
                "network": "1.1.1.1/32",
                "address": "1.1.1.1",
                "subnet": "/32",
            },
        ),
        (
            "1.1.1.1/32,",
            {
                "prefix": "",
                "suffix": ",",
                "network": "1.1.1.1/32",
                "address": "1.1.1.1",
                "subnet": "/32",
            },
        ),
        (
            "(1.1.1.1/32)",
            {
                "prefix": "(",
                "suffix": ")",
                "network": "1.1.1.1/32",
                "address": "1.1.1.1",
                "subnet": "/32",
            },
        ),
    ],
)
def test_parse_ipv4_address(data, expected):
    """Parser should extract IPv4 details."""
    parsed_network = NetworkParser(data)
    assert parsed_network.prefix == expected.get("prefix")
    assert parsed_network.suffix == expected.get("suffix")
    assert parsed_network.network== expected.get("network")
    assert parsed_network.address == expected.get("address")
    assert parsed_network.subnet == expected.get("subnet")

@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "1::a",
            {
                "prefix": "",
                "suffix": "",
                "network": "1::a",
                "address": "1::a",
                "subnet": "",
            },
        ),
        (
            "1::a/128",
            {
                "prefix": "",
                "suffix": "",
                "network": "1::a/128",
                "address": "1::a",
                "subnet": "/128",
            },
        ),
        (
            "1::a/128,",
            {
                "prefix": "",
                "suffix": ",",
                "network": "1::a/128",
                "address": "1::a",
                "subnet": "/128",
            },
        ),
        (
            "(1::a/128)",
            {
                "prefix": "(",
                "suffix": ")",
                "network": "1::a/128",
                "address": "1::a",
                "subnet": "/128",
            },
        ),
    ],
)
def test_parse_ipv6_address(data, expected):
    """Parser should extract IPv4 details."""
    parsed_network = NetworkParser(data)
    assert parsed_network.prefix == expected.get("prefix")
    assert parsed_network.suffix == expected.get("suffix")
    assert parsed_network.network== expected.get("network")
    assert parsed_network.address == expected.get("address")
    assert parsed_network.subnet == expected.get("subnet")
